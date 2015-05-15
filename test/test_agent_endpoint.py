import bootstrap
from mock_transport import MockTransport

import unittest
import unittest.mock
import datetime
import urllib.parse
import concurrent.futures
import cifparser

from mandelbrot.transport import *
from mandelbrot.agent.endpoint import Endpoint
from mandelbrot.model import construct
from mandelbrot.model.agent_metadata import AgentMetadata
from mandelbrot.model.registration import Registration
from mandelbrot.model.timestamp import Timestamp, UTC

class TestEndpoint(unittest.TestCase):

    url = urllib.parse.urlparse("mock://localhost")

    agent_id = cifparser.make_path('foo.local')

    def test_register_agent(self):
        "An Endpoint should register an Agent"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        transport = MockTransport(self.url, event_loop, executor)
        agent_metadata = AgentMetadata()
        agent_metadata.set_agent_id(cifparser.make_path('foo.agent'))
        agent_metadata.set_joined_on(construct(Timestamp, 0))
        agent_metadata.set_last_update(construct(Timestamp, 0))
        agent_metadata.set_lsn(1)
        transport.mock_create_item = unittest.mock.Mock(return_value=agent_metadata.destructure())
        endpoint = Endpoint(transport)
        registration = Registration()
        registration.set_agent_id(self.agent_id)
        future = asyncio.wait_for(endpoint.register_agent(registration), 5.0, loop=event_loop)
        response = event_loop.run_until_complete(future)
        self.assertDictEqual(response.destructure(), agent_metadata.destructure())
        self.assertEqual(transport.mock_create_item.call_count, 1)
        call_args,call_kwargs = transport.mock_create_item.call_args
        self.assertEqual(call_args[0], 'v2/agents')
