import asyncio
import signal
import logging
import requests
import pathlib

log = logging.getLogger("mandelbrot.command.start.supervisor")

from mandelbrot.registry import Registry
from mandelbrot.command.start.endpoint import Endpoint
from mandelbrot.command.start.processor import Processor
from mandelbrot.instance import open_instance

class Supervisor(object):
    """
    """
    def __init__(self, path, endpoint_executor, check_executor):
        """
        :param path:
        :type path: str
        :param endpoint_executor:
        :type endpoint_executor: concurrent.futures.Executor
        :param check_executor:
        :type check_executor: concurrent.futures.Executor
        """
        self.path = pathlib.Path(path)
        self.endpoint_executor = endpoint_executor
        self.check_executor = check_executor
        self.is_finished = False
        self.ignore_signals = False

    def run_forever(self):
        """
        """
        event_loop = asyncio.get_event_loop()
        shutdown_signal = asyncio.Event(loop=event_loop)

        # add handlers for the signals we are interested in
        event_loop.add_signal_handler(signal.SIGHUP, self.reload, shutdown_signal)
        event_loop.add_signal_handler(signal.SIGTERM, self.terminate, shutdown_signal)
        event_loop.add_signal_handler(signal.SIGINT, self.terminate, shutdown_signal)

        # load registry plugins
        registry = Registry()

        # loop forever until is_finished is True
        try:
            log.debug("--- starting agent process ---")
            while not self.is_finished:
                # open the instance at the specified path
                instance = open_instance(self.path)
                with instance.lock():
                    endpoint_url = instance.get_endpoint_url()
                # create the http endpoint
                session = requests.Session()
                endpoint = Endpoint(event_loop, endpoint_url, session, self.endpoint_executor)
                processor = Processor(event_loop, instance, registry, endpoint, self.check_executor)
                # enable signal catching
                self.ignore_signals = False
                # wait until the processor completes
                run_processor_until_signaled = processor.run_until_signaled(shutdown_signal)
                try:
                    event_loop.run_until_complete(run_processor_until_signaled)
                except Exception as e:
                    log.exception("processor throws exception: %s", e)
                    self.is_finished = True
                    self.ignore_signals = True
                # release resources
                instance.close()
                # reset the shutdown signal event
                shutdown_signal.clear()
        finally:
            log.debug("shutting down executors")
            self.check_executor.shutdown()
            self.endpoint_executor.shutdown()
            log.debug("shutting down event loop")
            event_loop.stop()
            event_loop.close()

    def reload(self, shutdown_signal):
        if not self.ignore_signals:
            self.ignore_signals = True
            log.info("--- reloading agent process ---")
            shutdown_signal.set()

    def terminate(self, shutdown_signal):
        if not self.ignore_signals:
            self.ignore_signals = True
            self.is_finished = True
            log.info("--- terminating agent process ---")
            shutdown_signal.set()
