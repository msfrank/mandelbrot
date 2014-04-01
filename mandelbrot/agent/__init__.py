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

from twisted.internet import reactor
from mandelbrot.plugin import PluginManager
from mandelbrot.agent.probe import ProbeScheduler
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG

logger = getLogger('mandelbrot.agent')

class Agent(object):
    """
    """
    def __init__(self):
        pass

    def configure(self, ns):
        # load configuration
        section = ns.section("agent")
        plugins = PluginManager()
        plugins.configure(section)
        self.probes = ProbeScheduler(plugins)
        # configure logging
        logconfigfile = section.getPath('log config file', "%s.logconfig" % ns.appname)
        if section.getBoolean("debug", False):
            startLogging(StdoutHandler(), DEBUG, logconfigfile)
        else:
            startLogging(None)

    def run(self):
        self.probes.startService()
        reactor.run()
        self.probes.stopService()
        return 0

    def printError(self, failure):
        import StringIO
        s = StringIO.StringIO()
        failure.printTraceback(s)
        logger.debug("caught exception: %s" % s.getvalue())
        reactor.stop()
