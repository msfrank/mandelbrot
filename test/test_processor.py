import bootstrap

import unittest
import asyncio
import concurrent.futures
import requests
import requests_mock

import mandelbrot.instance
import mandelbrot.registry
import mandelbrot.agent.processor
import mandelbrot.agent.evaluator
import mandelbrot.agent.endpoint
import mandelbrot.checks.dummy

class TestProcessor(unittest.TestCase):

    url = "mock://localhost"

    def test_process_check_and_submit_evaluation(self):
        "A Processor should process evaluations from a check and submit it to the endpoint"
        event_loop = asyncio.new_event_loop()
#        instance = mandelbrot.instance.Instance('/', 'test.process',
#            [mandelbrot.agent.evaluator.ScheduledCheck('id', mandelbrot.checks.dummy.AlwaysHealthy(), 1.0, 0, 0)]
#            )
        registry = mandelbrot.registry.Registry()
        submitted = []
        def text_callback(request, context):
            submitted.append(request)
            return ''
        mock = requests_mock.Adapter()
        mock.register_uri('POST', '/v2/systems/test.process/probes/id', status_code=200, text=text_callback)
        session = requests.Session()
        session.mount('mock', mock)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        endpoint = mandelbrot.agent.endpoint.Endpoint(event_loop, self.url, session, executor)
        processor = mandelbrot.agent.processor.Processor(event_loop, instance, registry, endpoint, executor)
        shutdown_signal = asyncio.Event()
        try:
            event_loop.run_until_complete(asyncio.wait_for(processor.run_until_signaled(shutdown_signal), 2.5, loop=event_loop))
        except concurrent.futures.TimeoutError:
            pass
        self.assertEquals(len(submitted), 3)
        request1 = submitted[0]
        self.assertEquals(request1.url, 'mock://localhost/v2/systems/test.process/probes/id')

