import bootstrap

import unittest
import asyncio
import requests
import requests_mock

import mandelbrot.agent.endpoint
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
        endpoint = mandelbrot.agent.endpoint.Endpoint(event_loop, self.url, 1, session)
        future = asyncio.wait_for(endpoint.get_agent('localhost.localdomain'), 5.0, loop=event_loop)
        response_item = event_loop.run_until_complete(future)
        self.assertIsInstance(response_item, mandelbrot.endpoint.ResponseItem)
        self.assertEqual(response_item.response.status_code, 200)
        self.assertEqual(response_item.item, {'foo': 'bar'})
