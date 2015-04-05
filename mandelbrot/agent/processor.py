import asyncio
import concurrent.futures
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

    @asyncio.coroutine
    def run_until_signaled(self, signal):
        """
        """
        shutdown_signal = self.event_loop.create_task(signal.wait())
        evaluator_task = self.event_loop.create_task(self.evaluator.run_until_signaled(signal))
        pending = set()
        pending.add(shutdown_signal)
        pending.add(self.evaluator.next_evaluation())

        while True:
            log.debug("waiting for %s", pending)
            done,pending = yield from asyncio.wait(pending, loop=self.event_loop,
                    return_when=concurrent.futures.FIRST_COMPLETED)
            log.debug("done=%s, pending=%s", done, pending)

            # if we were signaled, then break the loop
            if shutdown_signal.done():
                break

            # otherwise process the result of all completed futures
            done = [r.result() for r in done]
            for result in done:
                if isinstance(result, CheckResult):
                    check_id = result.scheduled_check.id
                    evaluation = result.result
                    log.debug("check %s submits evaluation %s", check_id, evaluation)
                    f = self.endpoint.submit_evaluation(self.instance.id, check_id, evaluation)
                    pending.add(f)
                    pending.add(self.evaluator.next_evaluation())
                elif isinstance(result, CheckFailed):
                    check_id = result.scheduled_check.id
                    log.debug("check %s failed: %s", check_id, str(result.failure))
                    pending.add(self.evaluator.next_evaluation())
                elif isinstance(result, requests.Response):
                    log.debug("endpoint responds %s", result.status_code)
                elif isinstance(result, Failure):
                    log.debug("endpoint raises %s", result.exception)

        # cancel all pending futures
        for f in pending:
            log.debug("cancelling pending future %s", f)
            f.cancel()

        # wait for evaluator to finish cleaning up
        yield from asyncio.wait_for(evaluator_task, None, loop=self.event_loop)
        self.evaluator = None

