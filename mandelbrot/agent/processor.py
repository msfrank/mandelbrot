import asyncio
import concurrent.futures
import logging
import requests

log = logging.getLogger("mandelbrot.agent.processor")

from mandelbrot.endpoint import Failure
from mandelbrot.agent.evaluator import ScheduledCheck, Evaluator, CheckResult, CheckFailed

class Processor(object):
    """
    """
    def __init__(self, event_loop, instance, registry, endpoint, executor):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param instance:
        :type instance: mandelbrot.instance.Instance
        :param registry:
        :type registry: mandelbrot.registry.Registry
        :param endpoint:
        :type endpoint: mandelbrot.agent.endpoint.Endpoint
        :param executor:
        :type executor: concurrent.futures.Executor
        """
        self.event_loop = event_loop
        self.instance = instance
        self.registry = registry
        self.endpoint = endpoint
        self.executor = executor

    @asyncio.coroutine
    def run_until_signaled(self, signal):
        """
        :param signal:
        :type signal: asyncio.Event
        """

        # get the agent id
        agent_id = self.instance.get_agent_id()

        # build the list of scheduled checks
        scheduled_checks = []
        for instance_check in self.instance.list_checks():
            factory_name, _, requirement = instance_check.check_type.partition(':')
            try:
                if requirement != '':
                    check_factory = self.registry.lookup_check(factory_name, requirement)
                else:
                    check_factory = self.registry.lookup_check(factory_name)
                check = check_factory()
                check.configure(instance_check.check_params)
                scheduled_check = ScheduledCheck(instance_check.check_id, check,
                    instance_check.delay, instance_check.offset, instance_check.jitter)
                scheduled_checks.append(scheduled_check)
            except Exception as e:
                log.warn("no check registered for type %s", instance_check.check_type)

        pending = set()

        # create the evaluator and run it in a task
        evaluator = Evaluator(self.event_loop, scheduled_checks, self.executor)
        evaluator_task = self.event_loop.create_task(evaluator.run_until_signaled(signal))
        pending.add(evaluator.next_evaluation())

        # create a future to wait for the shutdown signal
        shutdown_signal = self.event_loop.create_task(signal.wait())
        pending.add(shutdown_signal)

        while True:
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
                    log.debug("check %s submits evaluation %s to %s", check_id, evaluation, agent_id)
                    f = self.endpoint.submit_evaluation(agent_id, check_id, evaluation)
                    pending.add(f)
                    pending.add(evaluator.next_evaluation())
                elif isinstance(result, CheckFailed):
                    check_id = result.scheduled_check.id
                    log.debug("check %s failed: %s", check_id, str(result.failure))
                    pending.add(evaluator.next_evaluation())
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
