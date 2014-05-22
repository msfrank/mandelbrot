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

import os, sys, Queue, urlparse, pprint, datetime
from twisted.application.service import MultiService
from twisted.web.http_headers import Headers
from twisted.python.failure import Failure
from daemon import DaemonContext
from daemon.pidfile import TimeoutPIDLockFile
from setproctitle import setproctitle

from mandelbrot.plugin import PluginManager
from mandelbrot.agent.state import StateDatabase
from mandelbrot.agent.inventory import InventoryDatabase
from mandelbrot.agent.probes import ProbeScheduler, timedelta_to_seconds
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
        # configure registration
        self.maxattempts = section.get_int("max registration attempts", None)
        self.attemptwait = timedelta_to_seconds(section.get_timedelta("registration attempt delay", datetime.timedelta(minutes=5)))
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
        from twisted.internet import reactor
        self.agent = http.agent()
        headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
        registration = {'uri': self.inventory.uri, 'registration': self.inventory.registration} 
        # callbacks
        def on_retry(method, url, attempt):
            logger.debug("%s %s", method, url)
            defer = self.agent.request(method, url, headers, as_json(registration))
            defer.addBoth(on_response, method, url, attempt)
        def on_response(response, method, url, attempt):
            if isinstance(response, Failure):
                logger.error("registration attempt %i failed: %s", attempt, response.getErrorMessage())
                register(method, url, attempt + 1, self.attemptwait)
            else:
                logger.debug("registration attempt %i returned %i: %s", attempt, response.code, response.phrase)
                # registration accepted
                if response.code == 202:
                    self.state.put('uri', self.inventory.uri)
                    MultiService.startService(self)
                # system not found
                elif response.code == 404:
                    method = 'POST'
                    url = urlparse.urljoin(self.supervisor, 'objects/systems')
                    register(method, url, attempt + 1)
                # conflicts with existing system
                elif response.code == 409:
                    reactor.stop()
        def register(method, url, attempt, delay=None):
            if self.maxattempts is None or attempt <= self.maxattempts:
                if delay is not None:
                    reactor.callLater(self.attemptwait, on_retry, method, url, attempt)
                    logger.debug("retrying registration in %i seconds", delay)
                else:
                    on_retry(method, url, attempt)
            else:
                reactor.stop()
        # if we have previously stored uri as state, then use a PUT request
        if self.inventory.uri == self.state.get('uri'):
            logger.info("found cached system %s", self.state.get('uri'))
            method = 'PUT'
            url = urlparse.urljoin(self.supervisor, 'objects/systems/' + self.inventory.uri)
        # otherwise if this is a new registration, use a POST request
        else:
            method = 'POST'
            url = urlparse.urljoin(self.supervisor, 'objects/systems')
        logger.info("registering system %s with supervisor %s", registration['uri'], self.supervisor)
        logger.debug("submitting registration:\n%s", pprint.pformat(registration))
        # start the first attempt
        register(method, url, 1)

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
