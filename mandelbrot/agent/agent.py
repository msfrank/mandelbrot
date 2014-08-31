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
import pwd, grp
from twisted.application.service import MultiService
from twisted.web.http_headers import Headers
from twisted.python.failure import Failure
from daemon import DaemonContext
from daemon.pidfile import TimeoutPIDLockFile
from setproctitle import setproctitle

from mandelbrot.plugin import PluginManager
from mandelbrot.agent.registry import RegistryService
from mandelbrot.agent.scheduler import SchedulerService
from mandelbrot.agent.endpoints import EndpointWriter
from mandelbrot.agent.xmlrpc import XMLRPCService
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
        # configure endpoint
        self.scheduler = SchedulerService()
        self.scheduler.configure(ns)
        self.addService(self.scheduler)
        # configure endpoint
        self.endpoint = EndpointWriter(self.plugins)
        self.endpoint.configure(ns)
        self.addService(self.endpoint)
        # configure registry
        self.registry = RegistryService(self.plugins, self.scheduler, self.endpoint)
        self.registry.configure(ns)
        self.addService(self.registry)
        # configure xmlrpc
        self.xmlrpc = XMLRPCService(self)
        self.xmlrpc.configure(ns)
        self.addService(self.xmlrpc)
        # configure agent process
        self.foreground = section.get_bool("foreground", False)
        self.pidfile = section.get_path("pid file", os.path.join(defaults.get("RUN_DIR"), "agent.pid"))
        name = section.get_str("runtime user")
        if name is None:
            self.uid = None
        else:
            try:
                self.uid = pwd.getpwnam(name).pw_uid
            except:
                logger.warning("failed to get uid for runtime user %s", name)
                self.uid = None
        name = section.get_str("runtime group")
        if name is None:
            self.gid = None
        else:
            try:
                self.gid = grp.getrgnam(name).gr_gid
            except:
                logger.warning("failed to get gid for runtime group %s", name)
                self.gid = None
        # configure logging
        logconfigfile = section.get_path('log config file', "%s.logconfig" % ns.appname)
        if section.get_bool("debug", False):
            startLogging(StdoutHandler(), DEBUG, logconfigfile)
        else:
            startLogging(None)

    def run(self):
        logger.info("-- starting mandelbrot agent --")
        # execute any privileged subsystem code
        self.privilegedStartService()
        # set the process title
        setproctitle("mandelbrot-agent")
        # construct the daemon context
        daemon = DaemonContext()
        daemon.prevent_core = True
        daemon.chroot_directory = None
        daemon.working_directory = "/"
        if self.pidfile is not None:
            daemon.pidfile = TimeoutPIDLockFile(self.pidfile)
        if os.getuid() == 0:
            daemon.uid = self.uid
            daemon.gid = self.gid
        elif self.uid is not None or self.gid is not None:
            logger.warning("not dropping privileges, process uid is not 0")
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
