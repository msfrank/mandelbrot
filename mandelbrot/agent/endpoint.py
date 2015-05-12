import asyncio
import concurrent.futures
import contextlib
import logging

log = logging.getLogger("mandelbrot.agent.endpoint")

import mandelbrot.transport
from mandelbrot.transport import RetryLater

class Endpoint(object):
    """
    """
    def __init__(self, transport):
        """
        :param transport:
        :type transport: mandelbrot.transport.Transport
        """
        self.transport = transport

    @asyncio.coroutine
    def get_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :returns:
        :rtype:
        """
        path = 'v2/agents/' + str(agent_id)
        agent = yield from self.transport.get_item(path, {})
        return agent

    @asyncio.coroutine
    def register_agent(self, registration, num_tries):
        """
        :param registration:
        :type registration: mandelbrot.model.registration.Registration
        :param num_tries:
        :type num_tries: int
        """
        item = registration.destructure()
        tries_left = num_tries
        while tries_left:
            try:
                agent_metadata = yield from self.transport.create_item('v2/agents', item)
                return agent_metadata
            except RetryLater:
                tries_left -= 1
        raise RetryLater("failed to register after {} attempts".format(num_tries))

    @asyncio.coroutine
    def update_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        path = 'v2/agents/' + str(agent_id)
        agent_metadata = yield from self.transport.replace_item(path, registration.destructure())
        return agent_metadata

    @asyncio.coroutine
    def unregister_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        """
        yield from self.transport.delete_item('v2/agents/' + str(agent_id))
        return None

    @asyncio.coroutine
    def submit_evaluation(self, agent_id, check_id, evaluation):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :param evaluation:
        :type evaluation: mandelbrot.model.evaluation.Evaluation
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id)
        yield from self.transport.create_item(path, evaluation.destructure())
        return None

@contextlib.contextmanager
def make_endpoint(event_loop, endpoint_url, registry, transport_workers):
    """
    Create the transport and construct the agent endpoint.

    :param event_loop:
    :type event_loop: asyncio.AbstractEventLoop
    :param endpoint_url:
    :type endpoint_url: urllib.parse.ParseResult
    :param registry:
    :type registry: mandelbrot.registry.Registry
    :param num_workers:
    :type num_workers: int
    :return:
    """
    transport_factory = registry.lookup_factory(mandelbrot.transport.entry_point_type,
        endpoint_url.scheme, mandelbrot.transport.Transport)
    transport_executor = concurrent.futures.ThreadPoolExecutor(transport_workers)
    transport = transport_factory(endpoint_url, event_loop, transport_executor)
    log.debug("instantiating %s transport for %s", endpoint_url.scheme, endpoint_url)
    yield Endpoint(transport)
    transport.close()
    transport_executor.shutdown()
