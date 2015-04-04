import asyncio
import logging
import requests

log = logging.getLogger("mandelbrot.agent.processor")

from mandelbrot.endpoint import Failure
from mandelbrot.agent.evaluator import Evaluator, CheckResult, CheckFailed

class Processor(object):
    """
    """
    def __init__(self, event_loop, instance, endpoint, executor):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param instance:
        :type instance: mandelbrot.instance.Instance
        :param endpoint:
        :type endpoint: mandelbrot.agent.endpoint.Endpoint
        """
        self.event_loop = event_loop
        self.instance = instance
        self.endpoint = endpoint
        self.executor = executor
        self.evaluator = Evaluator(self.event_loop, self.instance.checks, self.executor)
        self.evaluator_task = None

    @asyncio.coroutine
    def run_forever(self):
        """
        """
        try:
            self.evaluator_task = self.event_loop.create_task(self.evaluator.run_forever())
            while True:
                result = yield from self.evaluator.next_evaluation()
                if result is None:
                    return
                if isinstance(result, CheckResult):
                    check_id = result.scheduled_check.id
                    evaluation = result.result
                    log.debug("check %s submits evaluation %s", check_id, evaluation)
                    f = self.endpoint.submit_evaluation(self.instance.id, check_id, evaluation)
                    f.add_done_callback(self.posted_evaluation)
                elif isinstance(result, CheckFailed):
                    check_id = result.scheduled_check.id
                    log.debug("check %s failed: %s", check_id, str(result.failure))
                else:
                    pass
        except asyncio.CancelledError:
            log.debug("processor has been cancelled")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.evaluator_task is not None:
            try:
                self.evaluator_task.cancel()
                self.event_loop.run_until_complete(self.evaluator_task)
            except asyncio.CancelledError:
                pass
        self.evaluator_task = None
        self.evaluator = None

    def posted_evaluation(self, f):
        result = f.result()
        if isinstance(result, requests.Response):
            log.debug("endpoint responds %s", result.status_code)
        elif isinstance(result, Failure):
            log.debug("endpoint raises %s", result.exception)
