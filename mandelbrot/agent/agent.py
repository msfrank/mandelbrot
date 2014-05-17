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

import os, sys, Queue, urlparse, pprint
from twisted.application.service import MultiService
from twisted.web.http_headers import Headers
from daemon import DaemonContext
from daemon.pidfile import TimeoutPIDLockFile
from setproctitle import setproctitle

from mandelbrot.plugin import PluginManager
from mandelbrot.agent.state import StateDatabase
from mandelbrot.agent.inventory import InventoryDatabase
from mandelbrot.agent.probes import ProbeScheduler
from mandelbrot.agent.endpoints import EndpointWriter
from mandelbrot.agent.xmlrpc import XMLRPCService
from mandelbrot.http import http, as_json
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG
from mandelbrot.defaults import defaults
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
        # configure the state db
        path = section.get_path("state directory", os.path.join(defaults["LOCALSTATE_DIR"], "mandelbrot"))
        self.state = StateDatabase(path)
        # load the inventory
        self.inventory = InventoryDatabase(self.plugins, self.state)
        self.inventory.configure(ns)
        # get agent process configuration
        self.foreground = section.get_bool("foreground", False)
        self.pidfile = section.get_path("pid file", None)
        # get supervisor configuration
        self.supervisor = section.get_str("supervisor url", ns.get_section('supervisor').get_str('supervisor url'))
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
        # configure xmlrpc
        self.xmlrpc = XMLRPCService(self)
        self.addService(self.xmlrpc)
        self.xmlrpc.configure(ns)
        # configure logging
        logconfigfile = section.get_path('log config file', "%s.logconfig" % ns.appname)
        if section.get_bool("debug", False):
            startLogging(StdoutHandler(), DEBUG, logconfigfile)
        else:
            startLogging(None)

    def startService(self):
        self.agent = http.agent()
        headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
        registration = {'uri': self.inventory.uri, 'registration': self.inventory.registration} 
        if self.inventory.uri == self.state.get('uri'):
            url = urlparse.urljoin(self.supervisor, 'objects/systems/' + self.inventory.uri)
            logger.debug("PUT %s\n%s", url, pprint.pformat(registration))
            defer = self.agent.request('PUT', url, headers, as_json(registration))
        else:
            url = urlparse.urljoin(self.supervisor, 'objects/systems')
            logger.debug("POST %s\n%s", url, pprint.pformat(registration))
            defer = self.agent.request('POST', url, headers, as_json(registration))
        defer.addCallbacks(self.on_response, self.on_failure)
        logger.info("registering system %s with supervisor %s", registration['uri'], self.supervisor)

    def on_response(self, response):
        logger.debug("registration returned %i %s", response.code, response.phrase)
        defer = http.read_body(response)
        defer.addCallbacks(self.on_registration, self.on_failure)

    def on_registration(self, registration):
        logger.debug("on_registration: %s", registration)
        self.state.put('uri', self.inventory.uri)
        MultiService.startService(self)

    def on_failure(self, failure):
        logger.error("registration failed: %s", failure.getErrorMessage())
        from twisted.internet import reactor
        reactor.stop()

    def run(self):
        logger.info("-- starting mandelbrot agent --")
        # execute any privileged subsystem code
        self.privilegedStartService()
        # set the process title
        setproctitle("mandelbrot-agent [%s]" % self.inventory.root.get_id())
        # construct the daemon context
        daemon = DaemonContext()
        daemon.prevent_core = True
        daemon.chroot_directory = None
        daemon.working_directory = "/"
        if self.pidfile is not None:
            daemon.pidfile = TimeoutPIDLockFile(self.pidfile)
        #daemon.uid = None
        #daemon.gid = None
        # FIXME: hack to ensure that fds stay open when passed to daemon context
        daemon.files_preserve = [x for x in xrange(64)]
        if self.foreground:
            daemon.detach_process = False
            daemon.stdin = sys.stdin
            daemon.stdout = sys.stdout
            daemon.stderr = sys.stderr
        else:
            daemon.detach_process = True
        with daemon:
            from twisted.internet import reactor
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
