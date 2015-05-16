import bootstrap

import unittest
import asyncio
import urllib.parse
import concurrent.futures
import cifparser
import requests
import requests_mock

from mandelbrot.transport.http import HttpTransport
from mandelbrot.agent.endpoint import Endpoint
from mandelbrot.model import construct
from mandelbrot.model.agent_metadata import AgentMetadata
from mandelbrot.model.registration import Registration
from mandelbrot.model.timestamp import Timestamp, now

class TestHttpTransport(unittest.TestCase):

    url = urllib.parse.urlparse("mock://localhost")

    def test_register_agent(self):
        "An HttpTransport should support registering an Agent"
        event_loop = asyncio.new_event_loop()
        mock = requests_mock.Adapter()
        agent_metadata = AgentMetadata()
        agent_metadata.set_agent_id(cifparser.make_path('foo.local'))
        timestamp = construct(Timestamp, 0)
        agent_metadata.set_joined_on(timestamp)
        agent_metadata.set_last_update(timestamp)
        agent_metadata.set_lsn(1)
        json = agent_metadata.destructure()
        mock.register_uri('POST', '/v2/agents', status_code=200, json=json)
        session = requests.Session()
        session.mount('mock', mock)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        transport = HttpTransport(self.url, event_loop, executor, session=session)
        endpoint = Endpoint(transport)
        registration = Registration()
        future = asyncio.wait_for(endpoint.register_agent(registration), 5.0, loop=event_loop)
        response = event_loop.run_until_complete(future)
        self.assertIsInstance(response, AgentMetadata)
        self.assertDictEqual(response.destructure(), agent_metadata.destructure())

    def test_update_agent(self):
        "An HttpTransport should support updating an Agent"
        event_loop = asyncio.new_event_loop()
        mock = requests_mock.Adapter()
        agent_id = cifparser.make_path('foo.local')
        agent_metadata = AgentMetadata()
        agent_metadata.set_agent_id(agent_id)
        timestamp = construct(Timestamp, 0)
        agent_metadata.set_joined_on(timestamp)
        agent_metadata.set_last_update(timestamp)
        agent_metadata.set_lsn(1)
        json = agent_metadata.destructure()
        mock.register_uri('PUT', '/v2/agents/' + str(agent_id), status_code=200, json=json)
        session = requests.Session()
        session.mount('mock', mock)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        transport = HttpTransport(self.url, event_loop, executor, session=session)
        endpoint = Endpoint(transport)
        registration = Registration()
        future = asyncio.wait_for(endpoint.update_agent(agent_id, registration), 5.0, loop=event_loop)
        response = event_loop.run_until_complete(future)
        self.assertIsInstance(response, AgentMetadata)
        self.assertDictEqual(response.destructure(), agent_metadata.destructure())
