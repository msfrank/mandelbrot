import bootstrap

import unittest
import asyncio
import concurrent.futures

import mandelbrot.agent.evaluator

class Check(object):
    def __init__(self, s):
        self.s = s
    def __call__(self):
        return self.s

class Failure(object):
    def __init__(self, s):
        self.s = s
    def __call__(self):
        raise Exception(self.s)

class TestEvaluator(unittest.TestCase):

    check1 = mandelbrot.agent.evaluator.ScheduledCheck('id1', Check("check1"), 1.2, 0.0, 0.0)

    check2 = mandelbrot.agent.evaluator.ScheduledCheck('id2', Check("check2"), 1.2, 0.4, 0.0)

    check3 = mandelbrot.agent.evaluator.ScheduledCheck('id3', Check("check3"), 1.2, 0.8, 0.0)

    failure1 = mandelbrot.agent.evaluator.ScheduledCheck('id4', Failure("failure1"), 1.0, 1.0, 0.0)
    
    def test_evaluate_checks_using_thread_pool(self):
        "An Evaluator should submit checks to a ThreadPoolExecutor and return the result"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        checks = [self.check1, self.check2, self.check3]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        event_loop.create_task(evaluator.run_forever())
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check1")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check2")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check3")

    def test_evaluate_checks_using_process_pool(self):
        "An Evaluator should submit checks to a ProcessPoolExecutor and return the result"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        checks = [self.check1, self.check2, self.check3]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        event_loop.create_task(evaluator.run_forever())
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check1")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check2")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check3")

    def test_handle_failed_check(self):
        "An Evaluator should return CheckFailed if the check raises an exception"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        checks = [self.check2, self.failure1]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        event_loop.create_task(evaluator.run_forever())
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.result, "check2")
        failure = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertIsInstance(failure, mandelbrot.agent.evaluator.CheckFailed)
        self.assertIs(failure.scheduled_check, self.failure1)
        self.assertIsInstance(failure.failure, Exception)
        self.assertEquals(str(failure.failure), "failure1")
