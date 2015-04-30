import bootstrap

import unittest
import asyncio
import concurrent.futures

import mandelbrot.agent.evaluator

class CheckSuccess(object):
    def __init__(self, s):
        self.s = s
    def execute(self, evaluation, context):
        evaluation.set_summary(self.s)
    def init(self):
        return None
    def fini(self, context):
        pass

class CheckException(object):
    def __init__(self, s):
        self.s = s
    def execute(self, evaluation, context):
        raise Exception(self.s)
    def init(self):
        return None
    def fini(self, context):
        pass

class CheckContext(object):
    def __init__(self, initial):
        self.current = initial
    def init(self):
        return {'current': self.current}
    def execute(self, evaluation, context):
        if context['current'] == self.current:
            evaluation.set_summary(str(context['current']))
        self.current += 2
        context['current'] += 2
    def fini(self, context):
        if context['current'] != self.current:
            raise Exception("context.current != self.current")

class TestEvaluator(unittest.TestCase):

    check1 = mandelbrot.agent.evaluator.ScheduledCheck('id1', CheckSuccess("check1"), 1.2, 0.0, 0.0)

    check2 = mandelbrot.agent.evaluator.ScheduledCheck('id2', CheckSuccess("check2"), 1.2, 0.4, 0.0)

    check3 = mandelbrot.agent.evaluator.ScheduledCheck('id3', CheckSuccess("check3"), 1.2, 0.8, 0.0)

    failure1 = mandelbrot.agent.evaluator.ScheduledCheck('id4', CheckException("failure1"), 1.0, 1.0, 0.0)

    context1 = mandelbrot.agent.evaluator.ScheduledCheck('id5', CheckContext(0), 1.0, 0.0, 0.0)

    context2 = mandelbrot.agent.evaluator.ScheduledCheck('id6', CheckContext(1), 1.0, 0.5, 0.0)
    
    def test_evaluate_checks_using_thread_pool(self):
        "An Evaluator should submit checks to a ThreadPoolExecutor and return the result"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        checks = [self.check1, self.check2, self.check3]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        shutdown_signal = asyncio.Event(loop=event_loop)
        event_loop.create_task(evaluator.run_until_signaled(shutdown_signal))
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check1")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check2")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check3")

    def test_evaluate_checks_using_process_pool(self):
        "An Evaluator should submit checks to a ProcessPoolExecutor and return the result"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        checks = [self.check1, self.check2, self.check3]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        shutdown_signal = asyncio.Event(loop=event_loop)
        event_loop.create_task(evaluator.run_until_signaled(shutdown_signal))
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check1")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check2")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check3")

    def test_handle_failed_check(self):
        "An Evaluator should continue processing if the check raises an exception"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        checks = [self.check2, self.failure1]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        shutdown_signal = asyncio.Event(loop=event_loop)
        event_loop.create_task(evaluator.run_until_signaled(shutdown_signal))
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check2")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "check2")

    def test_pass_check_context(self):
        "An Evaluator should pass the context between check invocations"
        event_loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        checks = [self.context1, self.context2]
        evaluator = mandelbrot.agent.evaluator.Evaluator(event_loop, checks, executor)
        shutdown_signal = asyncio.Event(loop=event_loop)
        event_loop.create_task(evaluator.run_until_signaled(shutdown_signal))
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "0")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "1")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "2")
        result = event_loop.run_until_complete(asyncio.wait_for(evaluator.next_evaluation(), 5.0, loop=event_loop))
        self.assertEquals(result.evaluation.get_summary(), "3")
