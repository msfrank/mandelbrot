import bootstrap
from mock_transport import MockTransport

import unittest
import unittest.mock
import urllib.parse
import asyncio
import concurrent.futures
import cifparser

from mandelbrot.transport import *
from mandelbrot.agent.endpoint import Endpoint
from mandelbrot.model.agent_metadata import AgentMetadata
from mandelbrot.model.registration import Registration

class TestEndpoint(unittest.TestCase):

    url = urllib.parse.urlparse("mock://localhost")

    agent_id = cifparser.make_path('foo.local')

    def test_register_agent(self):
        "An Endpoint should register an Agent"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        transport = MockTransport(self.url, event_loop, executor)
        agent_metadata = AgentMetadata()
        transport.mock_create_item = unittest.mock.Mock(return_value=agent_metadata)
        endpoint = Endpoint(transport)
        registration = Registration()
        registration.set_agent_id(self.agent_id)
        future = asyncio.wait_for(endpoint.register_agent(registration, 1), 5.0, loop=event_loop)
        response = event_loop.run_until_complete(future)
        self.assertIs(response, agent_metadata)
        self.assertEqual(transport.mock_create_item.call_count, 1)
        call_args,call_kwargs = transport.mock_create_item.call_args
        self.assertEqual(call_args[0], 'v2/agents')
