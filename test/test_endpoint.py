import bootstrap

import unittest
import asyncio
import concurrent.futures
import requests
import requests_mock

import mandelbrot.command.start.endpoint
import mandelbrot.endpoint

class TestEndpoint(unittest.TestCase):

    url = "mock://localhost"

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
        endpoint = mandelbrot.command.start.endpoint.Endpoint(event_loop, self.url, session, executor)
        future = asyncio.wait_for(endpoint.get_agent('localhost.localdomain'), 5.0, loop=event_loop)
        response = event_loop.run_until_complete(future)
        self.assertIsInstance(response, requests.Response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'foo': 'bar'})
