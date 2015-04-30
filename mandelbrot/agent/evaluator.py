import asyncio
import concurrent.futures
import contextlib
import logging

log = logging.getLogger("mandelbrot.agent.evaluator")

import mandelbrot.check
import mandelbrot.registry
from mandelbrot.model.evaluation import Evaluation
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

        # holds the context between invocations for each check
        check_contexts = {}
        # scheduled checks that are currently running on an executor
        checks_running = set()

        # schedule each check and run its init method
        scheduler = Scheduler(self.event_loop)
        for check in self.scheduled_checks:
            context = check.check.init()
            scheduler.schedule_task(check, check.delay, check.offset, check.jitter)
            check_contexts[check.check_id] = context
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
                # scheduled check is blocked
                if isinstance(result, ScheduledCheck) and result.check_id in checks_running:
                    log.warning("skipping check %s: previous invocation is still running",
                        result.check_id)
                    pending.add(scheduler.next_task())
                # scheduled check is ready to be run
                elif isinstance(result, ScheduledCheck):
                    check_id = result.check_id
                    check = result.check
                    context = check_contexts[check_id]
                    check_eval_ctx = CheckEvaluationContext(check_id, check, context)
                    log.debug("submitting check %s to executor with context %s", check_id, context)
                    execute_check = self.event_loop.run_in_executor(self.executor, check_eval_ctx.execute)
                    checks_running.add(check_id)
                    pending.add(execute_check)
                    pending.add(scheduler.next_task())
                # scheduled check has completed, queue it for processing
                elif isinstance(result, CheckEvaluationContext):
                    try:
                        check_id = result.check_id
                        evaluation = result.evaluation
                        context = result.context
                        checks_running.remove(check_id)
                        self.queue.put_nowait(CheckEvaluation(check_id, evaluation))
                        check_contexts[check_id] = context
                        log.debug("enqueuing evaluation for check %s", result.check_id)
                    except asyncio.QueueFull:
                        log.error("dropped evaluation for check %s, queue is full", result.check_id)
                # a scheduled check returns an error
                elif isinstance(result, EvaluationException):
                    log.error("check %s failed: %s", result.check_id, str(result.cause))
                elif isinstance(result, Exception):
                    log.error("check %s raises %s", result.check_id, str(result))

        # unscheduled all scheduled checks
        scheduler.unschedule_all()

        # cancel all pending futures
        for f in pending:
            log.debug("cancelling pending future %s", f)
            f.cancel()

        # run each check cleanup method
        for check in self.scheduled_checks:
            context = check_contexts[check.check_id]
            del check_contexts[check.check_id]
            check.check.fini(context)

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

class CheckEvaluationContext(object):
    """
    """
    def __init__(self, check_id, check, context):
        self._check = check
        self.check_id = check_id
        self.context = context
        self.evaluation = Evaluation()

    def execute(self):
        try:
            self._check.execute(self.evaluation, self.context)
            return self
        except Exception as e:
            return EvaluationException(self.check_id, e)

class EvaluationException(Exception):
    """
    """
    def __init__(self, check_id, cause):
        self.check_id = check_id
        self.cause = cause

class CheckEvaluation(object):
    """
    """
    def __init__(self, check_id, evaluation):
        self.check_id = check_id
        self.evaluation = evaluation

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
