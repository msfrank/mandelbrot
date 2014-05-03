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

import random, datetime, fnmatch
from threading import Thread
from twisted.application.service import MultiService
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.endpoints')

class EndpointWriter(MultiService):
    """
    """
    def __init__(self, plugins, deque):
        MultiService.__init__(self)
        self.setName("EndpointWriter")
        self.plugins = plugins
        self.endpoints = dict()
        self.deque = deque
        self.consumer = None

    def configure(self, ns):
        # configure generic endpoint parameters
        section = ns.get_section('endpoints')
        # configure individual endpoints
        for section in ns.find_sections('endpoint:'):
            endpointname = section.name[9:]
            logger.debug("creating endpoint %s", endpointname)
            endpointtype = section.get_str('endpoint type')
            accepts = section.get_list('accepts')
            if endpointtype is not None:
                try:
                    endpoint = self.plugins.newinstance('io.mandelbrot.endpoint', endpointtype)
                    endpoint.configure(section)
                    self.endpoints[endpointname] = (accepts,endpoint)
                    logger.debug("configured endpoint %s", endpointname)
                except Exception, e:
                    logger.warning("skipping endpoint %s: %s", endpointname, str(e))
            else:
                logger.warning("skipping endpoint %s: is missing endpoint type", endpointname)

    def startService(self):
        logger.debug("starting endpoint writer")
        self.consumer = MessageConsumer(self.deque, self.endpoints)
        self.consumer.start()

    def stopService(self):
        if self.consumer is not None:
            logger.debug("stopping message consumer thread")
            self.deque.put(MessageConsumer.TERMINATE)
            self.consumer.join()
        self.consumer = None
        logger.debug("stopped endpoint writer")

class MessageConsumer(Thread):
    """
    """
    def __init__(self, queue, endpoints):
        Thread.__init__(self, name="message-consumer-thread")
        self.daemon = True
        self._queue = queue
        self._endpoints = endpoints

    TERMINATE = 'terminate-thread'

    def run(self):
        while True:
            message = self._queue.get()
            if message is MessageConsumer.TERMINATE:
                break
            def endpoint_accepts_type(endpoint, filters, msgtype):
                if filters is None:
                    return True
                for pattern in filters:
                    if fnmatch.fnmatch(msgtype, pattern) == True:
                        return True
                return False
            for filters,endpoint in self._endpoints.values():
                if endpoint_accepts_type(endpoint, filters, message.msgtype):
                    endpoint.send(message)
        logger.debug("message-consumer-thread finishes")
