import asyncio
import logging

log = logging.getLogger("mandelbrot.agent.endpoint")

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
        :type agent_id: str
        :returns:
        :rtype:
        """
        path = 'v2/systems/' + agent_id
        agent = yield from self.transport.get_item(path, {})
        return agent

    @asyncio.coroutine
    def register_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: str
        :param registration:
        :type registration: mandelbrot.model.registration.Registration
        """
        yield from self.transport.create_item('v2/systems', registration.destructure())
        return None

    @asyncio.coroutine
    def update_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        path = 'v2/systems/' + agent_id
        yield from self.transport.replace_item(path, registration.destructure())
        return None

    @asyncio.coroutine
    def unregister_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: str
        """
        yield from self.transport.delete_item('v2/systems/' + agent_id)
        return None

    @asyncio.coroutine
    def submit_evaluation(self, agent_id, check_id, evaluation):
        """
        :param agent_id:
        :type agent_id: str
        :param check_id:
        :type check_id: str
        :param evaluation:
        :type evaluation: mandelbrot.model.evaluation.Evaluation
        """
        path = 'v2/systems/' + agent_id + '/probes/' + check_id
        yield from self.transport.create_item(path, evaluation.destructure())
        return None
