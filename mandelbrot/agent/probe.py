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
from twisted.internet.task import LoopingCall
from twisted.application.service import MultiService
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.probe')

class ProbeScheduler(MultiService):
    """
    """
    def __init__(self, plugins):
        MultiService.__init__(self)
        self.setName("ProbeScheduler")
        self.plugins = plugins
        self.probes = dict()

    def configure(self, ns):
        # configure generic probe parameters
        section = ns.section('probes')
        defaultinterval = section.gettimedelta("default probe interval")
        defaultsplay = section.gettimedelta("default probe splay")
        # configure individual probes
        for section in ns.sectionsLike('probe:'):
            probename = section.name[6:]
            probetype = section.getString('probe type')
            probeinterval = section.gettimedelta('probe interval', defaultinterval)
            probesplay = section.gettimedelta('probe splay', defaultsplay)
            if probetype is not None:
                try:
                    probe = self.plugins.newinstance('io.mandelbrot.probe', probetype)
                    probe.configure(section)
                    self.probes[probename] = ProbeRunner(probe, probename, probeinterval, probesplay)
                    logger.debug("configured probe:%s", probename)
                except Exception, e:
                    logger.warning("skipping probe:%s: %s", probename, str(e))
            else:
                logger.warning("skipping probe:%s: is missing probe type", probename)

    def startService(self):
        logger.debug("starting probe scheduler")
        for name,probe in self.probes.items():
            reactor.callLater(probe.splay, probe.start)

    def stopService(self):
        logger.debug("stopping probe scheduler")
        for name,probe in self.probes.items():
            probe.start()

class ProbeRunner(object):
    """
    """
    def __init__(self, probe, name, interval, splay):
        self.probe = probe
        self.name = name
        self.interval = interval
        self.splay = splay
        self._call = LoopingCall(probe.probe)

    def start(self):
        logger.debug("starting probe %s with interval %s", self.name, self.interval)
        self._call.start(self.interval, True)

    def stop(self):
        self._call.stop()
        logger.debug("stopped probe %s", self.name)
