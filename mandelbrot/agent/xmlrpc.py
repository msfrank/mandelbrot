
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

import time
from pesky.settings import ConfigureError
from twisted.application.service import Service
from twisted.web.xmlrpc import XMLRPC, withRequest
from twisted.web.server import Site
from mandelbrot.loggers import getLogger
from mandelbrot import versionstring

logger = getLogger('mandelbrot.agent.xmlrpc')

class XMLRPCService(Service):
    """
    """
    def __init__(self, agent):
        self.agent = agent
        self.api = API(agent)
        self.interface = None
        self.port = None
        self.listener = None

    def configure(self, ns):
        section = ns.get_section('agent')
        self.interface = section.get_str("xmlrpc tcp interface", 'localhost')
        self.port = section.get_int("xmlrpc tcp port", 9844)
        self.backlog = section.get_int("xmlrpc tcp backlog", 10)
        self.api.configure(ns)

    def startService(self):
        from twisted.internet import reactor
        self.listener = reactor.listenTCP(self.port, Site(self.api), backlog=self.backlog, interface=self.interface)

    def stopService(self):
        if self.listener is not None:
            return self.listener.stopListening()
        self.listener = None
        return None

class API(XMLRPC):
    """
    """
    def __init__(self, agent):
        XMLRPC.__init__(self)
        self.agent = agent
        self.started = time.time()

    def configure(self, ns):
        pass

    @withRequest
    def xmlrpc_getVersion(self, request):
        logger.debug("getVersion -> " + str(request))
        return versionstring()

    @withRequest
    def xmlrpc_getUptime(self, request):
        logger.debug("getUptime -> " + str(request))
        return long(time.time() - self.started)

    @withRequest
    def xmlrpc_getSpec(self, request):
        return self.agent.inventory.spec

    @withRequest
    def xmlrpc_getUri(self, request):
        return self.agent.inventory.uri
