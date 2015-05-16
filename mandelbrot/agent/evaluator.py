import asyncio
import concurrent.futures
import contextlib
import datetime
import logging

log = logging.getLogger("mandelbrot.agent.evaluator")

from mandelbrot.model.evaluation import Evaluation
from mandelbrot.model.timestamp import now
from mandelbrot.agent.scheduled_check import ScheduledCheck, make_scheduled_check
from mandelbrot.agent.scheduler import Scheduler

class CheckEvaluation(object):
    """
    The result of processing a check.
    """
    def __init__(self, check_id, evaluation):
        self.check_id = check_id
        self.evaluation = evaluation

class Evaluator(object):
    """
    The Evaluator takes a list of checks and invokes them according to
    the given schedule.  The checks are executed asynchronously on the
    specified executor.
    """
    def __init__(self, event_loop, scheduled_checks, executor):
        """
        :param event_loop: The event loop to use for scheduling and executing checks
        :type event_loop: asyncio.AbstractEventLoop
        :param scheduled_checks: The list of checks to evaluate
        :type scheduled_checks: list[ScheduledCheck]
        :param executor: The executor which asynchronously executes checks
        :type executor: concurrent.futures.Executor
        """
        self.event_loop = event_loop
        self.scheduled_checks = scheduled_checks
        self.executor = executor
        self.queue = asyncio.Queue(loop=event_loop)

    @asyncio.coroutine
    def run_until_signaled(self, signal):
        """
        Run the evaluator as an asynchronous task until the specified
        signal is set.

        :param signal: The signal which indicates termination
        :type signal: asyncio.Event
        :returns: a coroutine for the evaluator task
        :rtype: asyncio.coroutine
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
                    check_eval_ctx = EvaluationContext(check_id, check, context)
                    log.debug("submitting check %s to executor with context %s", check_id, context)
                    execute_check = self.event_loop.run_in_executor(self.executor, check_eval_ctx.execute)
                    checks_running.add(check_id)
                    pending.add(execute_check)
                    pending.add(scheduler.next_task())
                # scheduled check has completed, queue it for processing
                elif isinstance(result, EvaluationContext):
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
        Yields until the next check evaluation is available.

        :returns: A coroutine which yields the next check evaluation.
        :rtype: asyncio.coroutine
        """
        return self.queue.get()

@contextlib.contextmanager
def make_evaluator(event_loop, scheduled_checks, check_workers):
    """
    Create the evaluator within a context, and clean up associated
    resources when finished.

    :param event_loop: The event loop to use for scheduling and executing checks
    :type event_loop: asyncio.AbstractEventLoop
    :param scheduled_checks: The list of checks to evaluate
    :type scheduled_checks: list[ScheduledCheck]
    :param num_workers: The number of worker processes to create
    :type num_workers: int
    :returns: The Evaluator constructed from the specified scheduled checks
    """
    check_executor = concurrent.futures.ProcessPoolExecutor(check_workers)
    yield Evaluator(event_loop, scheduled_checks, check_executor)
    check_executor.shutdown()

class EvaluationContext(object):
    """
    Contains all context necessary to evaluate a check on an executor.
    This needs to be picklable, since we are likely using a process pool
    to execute the checks.
    """
    def __init__(self, check_id, check, context):
        """
        :param check_id: The check identifier, which is unique in the agent
        :type check_id: cifparser.Path
        :param check: The check instance
        :type check: mandelbrot.check.Check
        :param context: Data which persists between check executions
        :type context: object
        """
        self._check = check
        self.check_id = check_id
        self.context = context
        self.evaluation = None

    def execute(self):
        """
        Execute the check and return the entire context.  If the check
        raises an exception then return an EvaluationException with the
        exception inside instead.

        :returns: The EvaluationContext or an EvaluationException
        """
        try:
            self.evaluation = Evaluation()
            self.evaluation.set_timestamp(now())
            self._check.execute(self.evaluation, self.context)
            return self
        except Exception as e:
            return EvaluationException(self.check_id, e)

class EvaluationException(Exception):
    """
    Wraps any exception which is raised during check execution.
    """
    def __init__(self, check_id, cause):
        """
        :param check_id: The check identifier, which is unique in the agent
        :type check_id: cifparser.Path
        :param cause: The exception raised by the check
        :type cause: Exception
        """
        self.check_id = check_id
        self.cause = cause
