# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import Queue, random, datetime, urlparse
from threading import Thread
from twisted.application.service import MultiService
from pesky.settings import ConfigureError
from mandelbrot.plugin import PluginError
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.endpoints')

class EndpointWriter(MultiService):
    """
    """
    def __init__(self, plugins):
        MultiService.__init__(self)
        self.setName("EndpointWriter")
        self.plugins = plugins
        self.endpoint = None
        self.queue = None
        self.consumer = None

    def configure(self, ns):
        section = ns.get_section('agent')
        # get supervisor configuration
        self.supervisor = section.get_str("supervisor url", ns.get_section('supervisor').get_str('supervisor url'))
        url = urlparse.urlparse(self.supervisor)
        # create the internal agent queue
        queuesize = section.get_int("agent queue size", 4096)
        self.queue = Queue.Queue(maxsize=queuesize)
        logger.debug("created agent queue with size %i", queuesize)
        # configure the endpoint
        endpointtype = section.get_str('endpoint type')
        if endpointtype is None:
            try:
                self.endpoint = self.plugins.newinstance('io.mandelbrot.endpoint.scheme', url.scheme)
            except PluginError, e:
                raise ConfigureError("unknown endpoint scheme %s" % url.scheme)
        try:
            self.endpoint = self.plugins.newinstance('io.mandelbrot.endpoint', endpointtype)
        except PluginError, e:
                raise ConfigureError("unknown endpoint type %s" % endpointtype)
        section = ns.get_section('endpoint')
        self.endpoint.configure(self.supervisor, section)
        logger.debug("configured endpoint %s", self.supervisor)

    def startService(self):
        logger.debug("starting endpoint writer")
        self.consumer = MessageConsumer(self.queue, self.endpoint)
        self.consumer.start()

    def get_queue(self):
        return self.queue

    def register(self, uri, registration):
        return self.endpoint.register(uri, registration)

    def update(self, uri, registration):
        return self.endpoint.update(uri, registration)

    def unregister(self, uri):
        return self.endpoint.unregister(uri)
 
    def stopService(self):
        if self.consumer is not None:
            logger.debug("stopping message consumer thread")
            self.queue.put(MessageConsumer.TERMINATE)
            self.consumer.join()
        self.consumer = None
        logger.debug("stopped endpoint writer")

class MessageConsumer(Thread):
    """
    """
    def __init__(self, queue, endpoint):
        Thread.__init__(self, name="message-consumer-thread")
        self.daemon = True
        self._queue = queue
        self._endpoint = endpoint

    TERMINATE = 'terminate-thread'

    def run(self):
        while True:
            message = self._queue.get()
            if message is MessageConsumer.TERMINATE:
                break
            self._endpoint.send(message)
        logger.debug("message-consumer-thread finishes")
