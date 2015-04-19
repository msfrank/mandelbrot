import bootstrap

import unittest
import asyncio
import concurrent.futures
import pathlib
import shutil
import tempfile
import requests
import requests_mock

from mandelbrot.instance import create_instance, InstanceCheck
from mandelbrot.registry import Registry
from mandelbrot.command.start.processor import Processor
from mandelbrot.command.start.endpoint import Endpoint

class TestProcessor(unittest.TestCase):

    instance_path = pathlib.Path(tempfile.gettempdir(), 'fixture_TestProcessor')
    url = "mock://localhost"

    def setUp(self):
        self.instance_path.mkdir(parents=True)

    def tearDown(self):
        if self.instance_path.exists():
            shutil.rmtree(str(self.instance_path))

    def test_process_check_and_submit_evaluation(self):
        "A Processor should process evaluations from a check and submit it to the endpoint"
        event_loop = asyncio.new_event_loop()
        instance = create_instance(pathlib.Path(self.instance_path, "agent"))
        instance.set_endpoint_url(self.url)
        instance.set_agent_id("test.processor")
        instance.set_check(InstanceCheck('always.healthy', 'AlwaysHealthy', None, 1.0, 0, 0))
        registry = Registry()
        submitted = []
        def text_callback(request, context):
            submitted.append(request)
            return ''
        mock = requests_mock.Adapter()
        mock.register_uri('POST', '/v2/systems/test.processor/probes/always.healthy',
            status_code=200, text=text_callback)
        session = requests.Session()
        session.mount('mock', mock)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        endpoint = Endpoint(event_loop, self.url, session, executor)
        processor = Processor(event_loop, instance, registry, endpoint, executor)
        shutdown_signal = asyncio.Event()
        try:
            event_loop.run_until_complete(asyncio.wait_for(processor.run_until_signaled(shutdown_signal),
                2.5, loop=event_loop))
        except concurrent.futures.TimeoutError:
            pass
        self.assertEquals(len(submitted), 3)
        request1 = submitted[0]
        self.assertEquals(request1.url, 'mock://localhost/v2/systems/test.processor/probes/always.healthy')

