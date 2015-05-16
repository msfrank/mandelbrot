import bootstrap

import unittest
import unittest.mock
import asyncio
import concurrent.futures
import cifparser

from mandelbrot.transport import Transport
from mandelbrot.agent.endpoint import Endpoint
from mandelbrot.agent.evaluator import Evaluator, ScheduledCheck
from mandelbrot.agent.processor import process_evaluations
from mandelbrot.check import Check
from mandelbrot.model import construct
from mandelbrot.model.constants import CheckHealth
from mandelbrot.model.timestamp import Timestamp

class MockTransport(Transport):
    def __init__(self):
        self.mock_create_item = unittest.mock.Mock(return_value=None)
    @asyncio.coroutine
    def create_item(self, path, item):
        yield self.mock_create_item(path, item)

class MockCheck(Check):
    """
    """
    def __init__(self, *args, **kwargs):
        self.timestamp = construct(Timestamp, 0)
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarCheck"
    def get_behavior(self):
        return {}
    def execute(self, evaluation, context):
        evaluation.set_health(CheckHealth.HEALTHY)
        evaluation.set_summary("check returns healthy")
        evaluation.set_timestamp(self.timestamp)

class TestProcessor(unittest.TestCase):

    check1 = ScheduledCheck('id1', MockCheck(), 0.4, 0.0, 0.0)

    def test_process_evaluations(self):
        "process_evaluations() should submit evaluations to the endpoint"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        evaluator = Evaluator(event_loop, [self.check1], executor)
        agent_id = cifparser.make_path("foo.local")
        transport = MockTransport()
        endpoint = Endpoint(transport)
        shutdown_signal = asyncio.Event(loop=event_loop)
        event_loop.call_later(1.0, shutdown_signal.set)
        process_task = process_evaluations(event_loop, evaluator, agent_id, endpoint, shutdown_signal)
        event_loop.run_until_complete(asyncio.wait_for(process_task, 3.0, loop=event_loop))
        self.assertListEqual(transport.mock_create_item.call_args_list, [
            unittest.mock.call('v2/agents/foo.local/checks/id1', {'summary': 'check returns healthy', 'health': 'healthy', 'timestamp': 0}),
            unittest.mock.call('v2/agents/foo.local/checks/id1', {'summary': 'check returns healthy', 'health': 'healthy', 'timestamp': 0}),
            unittest.mock.call('v2/agents/foo.local/checks/id1', {'summary': 'check returns healthy', 'health': 'healthy', 'timestamp': 0}),
        ])
