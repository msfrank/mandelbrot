# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import concurrent.futures
import contextlib
import logging

log = logging.getLogger("mandelbrot.agent.endpoint")

import mandelbrot.transport
from mandelbrot.transport import RetryLater
from mandelbrot.model.agent_metadata import AgentMetadata
from mandelbrot.model.registration import Registration
from mandelbrot.model import construct

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
        registration = yield from self.transport.get_item(path, {})
        return construct(Registration, registration)

    @asyncio.coroutine
    def register_agent(self, registration):
        """
        :param registration:
        :type registration: mandelbrot.model.registration.Registration
        """
        item = registration.destructure()
        agent_metadata = yield from self.transport.create_item('v2/agents', item)
        return construct(AgentMetadata, agent_metadata)

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
        return construct(AgentMetadata, agent_metadata)

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
