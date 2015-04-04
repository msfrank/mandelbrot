import asyncio
import signal
import logging
import requests

log = logging.getLogger("mandelbrot.agent.supervisor")

from mandelbrot.agent.endpoint import Endpoint
from mandelbrot.agent.processor import Processor
from mandelbrot.instance import open_instance

class Supervisor(object):
    """
    """
    def __init__(self, path, endpoint_url, endpoint_executor, check_executor):
        """
        :param path:
        :type path: str
        :param endpoint_url:
        :type endpoint_url: str
        :param endpoint_executor:
        :type endpoint_executor: concurrent.futures.Executor
        :param check_executor:
        :type check_executor: concurrent.futures.Executor
        """
        self.path = path
        self.endpoint_url = endpoint_url
        self.endpoint_executor = endpoint_executor
        self.check_executor = check_executor
        self.event_loop = asyncio.get_event_loop()
        self.processor_task = None
        self.is_finished = False
        self.ignore_signals = False

    def run_forever(self):
        """
        """
        # add handlers for the signals we are interested in
        self.event_loop.add_signal_handler(signal.SIGHUP, self.reload)
        self.event_loop.add_signal_handler(signal.SIGTERM, self.terminate)
        self.event_loop.add_signal_handler(signal.SIGINT, self.terminate)
        # create the http endpoint
        session = requests.Session()
        endpoint = Endpoint(self.event_loop, self.endpoint_url, session, self.endpoint_executor)
        # loop forever until is_finished is True 
        try:
            log.debug("--- starting agent process ---")
            while not self.is_finished:
                # create a new agent and run it forever until it completes
                instance = open_instance(self.path, 0o600)
                processor = Processor(self.event_loop, instance, endpoint, self.check_executor)
                self.processor_task = self.event_loop.create_task(processor.run_forever())
                # enable signal catching
                self.ignore_signals = False
                # wait until the processor completes
                self.event_loop.run_until_complete(self.processor_task)
                # check the result of the task
                try:
                    result = self.processor_task.result()
                    raise ValueError("agent returned unexpected value {0]".format(result))
                # we expect CancelledError
                except asyncio.CancelledError:
                    pass
                # any other condition is fatal
                except:
                    raise
        finally:
            log.debug("shutting down executors")
            self.check_executor.shutdown()
            self.endpoint_executor.shutdown()
            log.debug("shutting down executors")
            self.event_loop.stop()
            self.event_loop.close()
            self.event_loop = None

    def reload(self):
        if not self.ignore_signals:
            self.ignore_signals = True
            log.info("--- reloading agent process ---")
            self.processor_task.cancel()

    def terminate(self):
        if not self.ignore_signals:
            self.ignore_signals = True
            self.is_finished = True
            log.info("--- terminating agent process ---")
            self.processor_task.cancel()
