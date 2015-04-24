import asyncio
import concurrent.futures
import datetime
import pprint
import logging
import requests

from cifparser import or_default

log = logging.getLogger("mandelbrot.agent.processor")

from mandelbrot.model.registration import Registration
from mandelbrot.model.check import Check
from mandelbrot.transport import TransportException, RetryLater
from mandelbrot.transport.http import HttpTransport
from mandelbrot.agent.endpoint import Endpoint
from mandelbrot.agent.evaluator import make_scheduled_check, Evaluator, CheckResult, CheckFailed

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
            factory_name, _, requirement = instance_check.check_type.partition(':')
            try:
                scheduled_check = make_scheduled_check(instance_check, self.registry)
                scheduled_checks.append(scheduled_check)
            except Exception as e:
                log.warn("no check registered for type %s", instance_check.check_type)

        # construct the registration
        registration = Registration()
        registration.set_agent_type("mandelbrot")
        registration.set_agent_id(agent_id)
        for meta_name,meta_value in metadata:
            registration.set_meta_value(meta_name, meta_value)

        # note that scheduled_checks is ordered by check_id
        for scheduled_check in scheduled_checks:
            check_id = scheduled_check.check_id
            check = Check()
            check.set_check_id(check_id)
            # check must implement get_behavior_type()
            check.set_behavior_type(scheduled_check.check.get_behavior_type())
            # if policy parameters aren't specified, use agent or application default
            join_timeout = or_default(default_join_timeout, scheduled_check.check.get_join_timeout)
            check.set_join_timeout(join_timeout)
            alert_timeout = or_default(default_alert_timeout, scheduled_check.check.get_alert_timeout)
            check.set_alert_timeout(alert_timeout)
            probe_timeout = or_default(default_probe_timeout, scheduled_check.check.get_probe_timeout)
            check.set_probe_timeout(probe_timeout)
            retirement_age = or_default(default_retirement_age, scheduled_check.check.get_retirement_age)
            check.set_retirement_age(retirement_age)
            registration.set_check(check_id, check)

        log.debug("registration for %s:\n%s", agent_id, pprint.pformat(registration.destructure(),
            indent=4, width=120, compact=False))

        transport_executor = None
        check_executor = None

        try:

            # create the transport and construct the agent endpoint
            transport_workers = 10
            transport_executor = concurrent.futures.ThreadPoolExecutor(transport_workers)
            transport = HttpTransport(endpoint_url, self.event_loop, transport_executor)
            endpoint = Endpoint(transport)

            # register agent with the endpoint
            log.debug("registering %s with endpoint", agent_id)
            retries_left = 3
            while True:
                if not retries_left:
                    raise Exception("failed to register")
                try:
                    yield from endpoint.register_agent(agent_id, registration)
                except RetryLater:
                    retries_left -= 1
                except Exception as e:
                    log.debug("endpoint responded %s", e)
                    raise

            # pending contains all the futures we are waiting for
            pending = set()

            # create the evaluator and run it in a task
            check_workers = 10
            check_executor = concurrent.futures.ProcessPoolExecutor(check_workers)
            evaluator = Evaluator(self.event_loop, scheduled_checks, check_executor)
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
                results = []
                for f in done:
                    try:
                        results.append(f.result())
                    except Exception as e:
                        results.append(e)
                for result in results:
                    if isinstance(result, CheckResult):
                        check_id = result.scheduled_check.check_id
                        evaluation = result.result
                        log.debug("check %s submits evaluation %s", check_id, evaluation)
                        pending.add(endpoint.submit_evaluation(agent_id, check_id, evaluation))
                        pending.add(evaluator.next_evaluation())
                    elif isinstance(result, CheckFailed):
                        check_id = result.scheduled_check.id
                        log.error("check %s failed: %s", check_id, str(result.failure))
                        pending.add(evaluator.next_evaluation())
                    elif isinstance(result, TransportException):
                        log.error("endpoint responds %s", result)
                    elif isinstance(result, None):
                        log.debug("endpoint accepted evaluation")

            # cancel all pending futures
            for f in pending:
                log.debug("cancelling pending future %s", f)
                f.cancel()

            # wait for evaluator to finish cleaning up
            yield from asyncio.wait_for(evaluator_task, None, loop=self.event_loop)

        finally:
            log.debug("shutting down executors")
            if transport_executor is not None:
                transport_executor.shutdown()
            if check_executor is not None:
                check_executor.shutdown()
