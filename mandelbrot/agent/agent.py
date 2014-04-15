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

import Queue, urlparse, pprint
from twisted.internet import reactor
from twisted.application.service import MultiService
from twisted.web.client import Agent as HttpAgent
from twisted.web.http_headers import Headers

from mandelbrot.plugin import PluginManager
from mandelbrot.agent.inventory import InventoryDatabase
from mandelbrot.agent.probes import ProbeScheduler
from mandelbrot.agent.endpoints import EndpointWriter
from mandelbrot.agent.http import JsonProducer
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG
from mandelbrot import versionstring

logger = getLogger('mandelbrot.agent.agent')

class Agent(MultiService):
    """
    """
    def __init__(self):
        MultiService.__init__(self)
        self.setName('Agent')

    def configure(self, ns):
        logger.debug("-- configuring mandelbrot agent --")
        # load configuration
        section = ns.get_section("agent")
        self.plugins = PluginManager()
        self.plugins.configure(section)
        # load the inventory
        self.inventory = InventoryDatabase(self.plugins)
        self.inventory.configure(ns)
        # get supervisor configuration
        self.supervisor = section.get_str("supervisor url")
        # create the internal agent queue
        queuesize = section.get_int("agent queue size", 4096)
        self.queue = Queue.Queue(maxsize=queuesize)
        logger.debug("created agent queue with size %i", queuesize)
        # configure probes
        self.probes = ProbeScheduler(self.inventory, self.queue)
        self.addService(self.probes)
        self.probes.configure(ns)
        # configure endpoints
        self.endpoints = EndpointWriter(self.plugins, self.queue)
        self.addService(self.endpoints)
        self.endpoints.configure(ns)
        # configure logging
        logconfigfile = section.get_path('log config file', "%s.logconfig" % ns.appname)
        if section.get_bool("debug", False):
            startLogging(StdoutHandler(), DEBUG, logconfigfile)
        else:
            startLogging(None)

    def makeregistration(self):
        def makespec(obj):
            children = {}
            for name,child in obj.children.items():
                children[name] = makespec(child)
            return {'objectType': obj.get_type(), 'metaData': obj.get_metadata(), 'children': children}
        return {'uri': self.inventory.root.get_id(), 'spec': makespec(self.inventory.root)} 

    def startService(self):
        # start child services 
        MultiService.startService(self)
        # register with supervisor
        registration = self.makeregistration()
        url = urlparse.urljoin(self.supervisor, '1/registry')
        logger.info("registering system %s with supervisor %s", registration['uri'], self.supervisor)
        self.agent = HttpAgent(reactor)
        headers = Headers({
            'Content-Type': ['application/json'],
            'User-Agent': ['mandelbrot-agent/' + versionstring()]
        })
        logger.debug("POST %s\n%s", url, pprint.pformat(registration))
        defer = self.agent.request('POST', url, headers, JsonProducer(registration))
        defer.addCallbacks(self.onRegistration, self.onFailure)

    def onRegistration(self, response):
        logger.debug("registration returned %i %s", response.code, response.phrase)
        expires = response.headers.getRawHeaders('Expires')
        cacheControl = response.headers.getRawHeaders('Cache-Control')

    def onFailure(self, failure):
        logger.debug("registration failed: %s" % failure.getErrorMessage())

    def run(self):
        logger.info("-- starting mandelbrot agent --")
        self.privilegedStartService()
        self.startService()
        reactor.run()
        logger.info("-- stopping mandelbrot agent --")
        self.stopService()
        logger.info("-- stopped mandelbrot agent --")
        return 0

    def printError(self, failure):
        import StringIO
        s = StringIO.StringIO()
        failure.printTraceback(s)
        logger.debug("caught exception: %s" % s.getvalue())
        reactor.stop()
