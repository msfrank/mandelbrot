import asyncio
import concurrent.futures
import datetime
import logging

log = logging.getLogger("mandelbrot.agent.processor")

from mandelbrot.agent.endpoint import make_endpoint
from mandelbrot.agent.registration import make_registration
from mandelbrot.agent.evaluator import make_scheduled_check, make_evaluator, CheckEvaluation
from mandelbrot.transport import TransportException

default_join_timeout = datetime.timedelta(minutes=5)
default_probe_timeout = datetime.timedelta(minutes=1)
default_alert_timeout = datetime.timedelta(minutes=2)
default_retirement_age = datetime.timedelta(days=1)

class Processor(object):
    """
    """
    def __init__(self, event_loop, instance, registry, settings):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param instance:
        :type instance: mandelbrot.instance.Instance
        :param registry:
        :type registry: mandelbrot.registry.Registry
        :param settings:
        :type settings: cifparser.Namespace
        """
        self.event_loop = event_loop
        self.instance = instance
        self.registry = registry
        self.settings = settings

    @asyncio.coroutine
    def run_until_signaled(self, signal):
        """
        Run the Processor until the specified signal is set.

        :param signal:
        :type signal: asyncio.Event
        """

        # load configuration from the instance
        with self.instance.lock():
            agent_id = self.instance.get_agent_id()
            endpoint_url = self.instance.get_endpoint_url()
            checks = sorted(self.instance.list_checks(), key=lambda check: check.check_id)
            metadata = list(self.instance.list_metadata())
        log.debug("loading instance %s", agent_id)

        # build the list of scheduled checks
        scheduled_checks = []
        for instance_check in checks:
            try:
                scheduled_check = make_scheduled_check(instance_check, self.registry)
                scheduled_checks.append(scheduled_check)
            except Exception as e:
                log.warn("no check registered for type %s", instance_check.check_type)

        # construct the registration
        registration = make_registration(agent_id, metadata, scheduled_checks)

        # construct the endpoint
        log.debug("constructing endpoint %s", endpoint_url)
        with make_endpoint(self.event_loop, endpoint_url, self.registry, 10) as endpoint:

            # register agent with the endpoint
            log.debug("registering %s with endpoint", agent_id)
            yield from endpoint.register_agent(registration, 1)

            # construct the evaluator
            with make_evaluator(self.event_loop, scheduled_checks, 10) as evaluator:

                # run until processor_task completes
                processor_task = process_evaluations(self.event_loop,
                    evaluator, agent_id, endpoint, signal)
                yield from asyncio.wait_for(processor_task, None, loop=self.event_loop)

@asyncio.coroutine
def process_evaluations(event_loop, evaluator, agent_id, endpoint, signal):
    """
    Process evaluations until the specified signal is set.

    :param event_loop:
    :type event_loop: asyncio.AbstractEventLoop
    :param evaluator:
    :type evaluator: mandelbrot.agent.evaluator.Evaluator
    :param agent_id:
    :type agent_id: cifparser.Path
    :param endpoint:
    :type endpoint: mandelbrot.agent.endpoint.Endpoint
    :param signal:
    :type signal: asyncio.Event
    """
    # pending contains all the futures we are waiting for
    pending = set()

    # create a future to wait for the shutdown signal
    shutdown_signal = event_loop.create_task(signal.wait())
    pending.add(shutdown_signal)

    # start the evaluator and wait for the first evaluation
    evaluator_task = event_loop.create_task(evaluator.run_until_signaled(signal))
    pending.add(evaluator.next_evaluation())

    # loop until we receive the shutdown signal
    while True:
        done,pending = yield from asyncio.wait(pending, loop=event_loop,
            return_when=concurrent.futures.FIRST_COMPLETED)
        log.debug("done=%s, pending=%s", done, pending)

        # if we were signaled, then break the loop
        if shutdown_signal.done():
            break

        # otherwise process the result of all completed futures
        results = []
        for f in done:
            try:
                results.append(f.result())
            except Exception as e:
                results.append(e)
        for result in results:
            if isinstance(result, CheckEvaluation):
                check_id = result.check_id
                evaluation = result.evaluation
                log.debug("check %s submits evaluation %s", check_id, evaluation)
                pending.add(endpoint.submit_evaluation(agent_id, check_id, evaluation))
                pending.add(evaluator.next_evaluation())
            elif isinstance(result, TransportException):
                log.error("endpoint responds %s", result)
            elif isinstance(result, Exception):
                log.error("endpoint raises %s", result)
            elif result is None:
                log.debug("endpoint accepted evaluation")

    # cancel all pending futures
    for f in pending:
        log.debug("cancelling pending future %s", f)
        f.cancel()

    # wait for evaluator to finish cleaning up
    yield from asyncio.wait_for(evaluator_task, None, loop=event_loop)
