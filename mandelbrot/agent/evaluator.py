import asyncio
import concurrent.futures
import logging

log = logging.getLogger("mandelbrot.agent.evaluator")

from mandelbrot.agent.scheduler import Scheduler

class Evaluator(object):
    """
    """
    def __init__(self, event_loop, checks, executor):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param checks:
        :type checks: list[ScheduledCheck]
        :param executor:
        :type executor: concurrent.futures.Executor
        """
        self.event_loop = event_loop
        self.executor = executor
        self.queue = asyncio.Queue(loop=event_loop)
        self.scheduler = Scheduler(event_loop)
        for check in checks:
            self.scheduler.schedule_task(check, check.delay, check.offset, check.jitter)

    @asyncio.coroutine
    def run_until_signaled(self, signal):
        """
        """
        shutdown_signal = self.event_loop.create_task(signal.wait())
        pending = set()
        pending.add(shutdown_signal)
        pending.add(self.scheduler.next_task())

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

                if isinstance(result, ScheduledCheck):
                    log.debug("submitting %s to executor", result)
                    execute_check = self.event_loop.run_in_executor(self.executor, result)
                    pending.add(execute_check)
                    pending.add(self.scheduler.next_task())
                else:
                    try:
                        self.queue.put_nowait(result)
                    except asyncio.QueueFull:
                        log.error("dropping check evaluation, queue is full")

        # cancel all pending futures
        for f in pending:
            log.debug("cancelling pending future %s", f)
            f.cancel()

    def next_evaluation(self):
        """
        :returns: The next completed check evaluation.
        :rtype: callable
        """
        return self.queue.get()

class ScheduledCheck(object):
    """
    """
    def __init__(self, id, check, delay, offset, jitter):
        """
        :param id:
        :type id: str
        :param check:
        :type check: mandelbrot.checks.Check
        :param delay:
        :type delay: float
        :param offset:
        :type offset: float
        :param jitter:
        :type jitter: float
        """
        self.id = id
        self.check = check
        self.delay = delay
        self.offset = offset
        self.jitter = jitter

    def __call__(self, *args, **kwargs):
        try:
            return CheckResult(self, self.check())
        except Exception as e:
            return CheckFailed(self, e)

class CheckResult(object):
    """
    """
    def __init__(self, scheduled_check, result):
        """
        :param scheduled_check:
        :type scheduled_check: ScheduledCheck
        :param result:
        :type result: object
        """
        self.scheduled_check = scheduled_check
        self.result = result

class CheckFailed(object):
    """
    """
    def __init__(self, scheduled_check, failure):
        """
        :param scheduled_check:
        :type scheduled_check: ScheduledCheck
        :param failure:
        :type failure: Exception
        """
        self.scheduled_check = scheduled_check
        self.failure = failure
