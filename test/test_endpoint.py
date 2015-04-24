import bootstrap

import unittest
import asyncio
import urllib.parse
import concurrent.futures
import requests
import requests_mock

from mandelbrot.transport.http import HttpTransport
from mandelbrot.agent.endpoint import Endpoint

class TestEndpoint(unittest.TestCase):

    url = urllib.parse.urlparse("mock://localhost")

    def test_register_agent(self):
        "An Endpoint should register an Agent"
        event_loop = asyncio.new_event_loop()
        mock = requests_mock.Adapter()
        mock.register_uri('GET', '/v2/systems/localhost.localdomain', status_code=200,
            json={'foo': 'bar'}
            )
        session = requests.Session()
        session.mount('mock', mock)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        transport = HttpTransport(self.url, event_loop, executor, session=session)
        endpoint = Endpoint(transport)
        future = asyncio.wait_for(endpoint.get_agent('localhost.localdomain'), 5.0, loop=event_loop)
        response = event_loop.run_until_complete(future)
        self.assertDictEqual(response, {'foo': 'bar'})
