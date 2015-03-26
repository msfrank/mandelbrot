import bootstrap

import unittest
import asyncio
import concurrent.futures

import mandelbrot.agent.evaluator

class TestEvaluator(unittest.TestCase):

    check1 = mandelbrot.agent.evaluator.ScheduledCheck(lambda: "check1", 1.2, 0.0, 0.0)
    check2 = mandelbrot.agent.evaluator.ScheduledCheck(lambda: "check2", 1.2, 0.4, 0.0)
    check3 = mandelbrot.agent.evaluator.ScheduledCheck(lambda: "check3", 1.2, 0.8, 0.0)

    def test_evaluate_checks(self):
        "An Evaluator should submit checks to an executor and return the result"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        checks = [self.check1, self.check2, self.check3]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, executor, checks)
        event_loop.create_task(evaluator.run_forever())
        evaluation = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(evaluation, "check1")
        evaluation = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(evaluation, "check2")
        evaluation = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(evaluation, "check3")
