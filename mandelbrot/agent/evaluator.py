import asyncio
import concurrent.futures
import contextlib
import logging

log = logging.getLogger("mandelbrot.agent.evaluator")

import mandelbrot.check
import mandelbrot.registry
from mandelbrot.agent.scheduler import Scheduler

class Evaluator(object):
    """
    """
    def __init__(self, event_loop, scheduled_checks, executor):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param scheduled_checks:
        :type scheduled_checks: list[ScheduledCheck]
        :param executor:
        :type executor: concurrent.futures.Executor
        """
        self.event_loop = event_loop
        self.scheduled_checks = scheduled_checks
        self.executor = executor
        self.queue = asyncio.Queue(loop=event_loop)

    @asyncio.coroutine
    def run_until_signaled(self, signal):
        """
        """
        pending = set()
        shutdown_signal = self.event_loop.create_task(signal.wait())
        pending.add(shutdown_signal)

        # schedule each check and run its init method
        scheduler = Scheduler(self.event_loop)
        for check in self.scheduled_checks:
            check.check.init()
            scheduler.schedule_task(check, check.delay, check.offset, check.jitter)
        pending.add(scheduler.next_task())

        # loop executing each check according to its schedule
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
                    pending.add(scheduler.next_task())
                else:
                    try:
                        self.queue.put_nowait(result)
                    except asyncio.QueueFull:
                        log.error("dropping check evaluation, queue is full")

        # unscheduled all scheduled checks
        scheduler.unschedule_all()

        # cancel all pending futures
        for f in pending:
            log.debug("cancelling pending future %s", f)
            f.cancel()

        # run each check cleanup method
        for check in self.scheduled_checks:
            check.check.fini()

    def next_evaluation(self):
        """
        :returns: The next completed check evaluation.
        :rtype: callable
        """
        return self.queue.get()

@contextlib.contextmanager
def make_evaluator(event_loop, scheduled_checks, check_workers):
    """
    Create the transport and construct the agent endpoint.

    :param event_loop:
    :type event_loop: asyncio.AbstractEventLoop
    :param endpoint_url:
    :type endpoint_url: urllib.parse.ParseResult
    :param registry:
    :type registry: mandelbrot.registry.Registry
    :param num_workers:
    :type num_workers: int
    :return:
    """
    check_executor = concurrent.futures.ProcessPoolExecutor(check_workers)
    yield Evaluator(event_loop, scheduled_checks, check_executor)
    check_executor.shutdown()

class ScheduledCheck(object):
    """
    """
    def __init__(self, check_id, check, delay, offset, jitter):
        """
        :param check_id:
        :type check_id: str
        :param check:
        :type check: mandelbrot.checks.Check
        :param delay:
        :type delay: float
        :param offset:
        :type offset: float
        :param jitter:
        :type jitter: float
        """
        self.check_id = check_id
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

def make_scheduled_check(instance_check, registry):
    """

    :param instance_check:
    :type instance_check: mandelbrot.instance.InstanceCheck
    :param registry:
    :type registry: mandelbrot.registry.Registry
    :rtype: ScheduledCheck
    """
    factory_name, _, requirement = instance_check.check_type.partition(':')
    if requirement == '':
        requirement = mandelbrot.registry.require_mandelbrot
    check_factory = registry.lookup_factory(mandelbrot.check.entry_point_type,
        factory_name, mandelbrot.check.Check, requirement)
    check = check_factory(instance_check.check_params)
    log.debug("instantiating check %s with requirement '%s'",
        instance_check.check_id, instance_check.check_type)
    scheduled_check = ScheduledCheck(instance_check.check_id, check,
        instance_check.delay, instance_check.offset, instance_check.jitter)
    return scheduled_check
