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

import random, datetime, Queue
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.application.service import Service
from pesky.settings import ConfigureError
from mandelbrot.evaluation import Evaluation
from mandelbrot.message import StatusMessage,MetricsMessage,EventsMessage,SnapshotMessage
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.probes')

class ProbeScheduler(Service):
    """
    """
    def __init__(self, inventory, deque):
        self.setName("ProbeScheduler")
        self.inventory = inventory
        self.probes = dict()
        self.deque = deque

    def configure(self, ns):
        # configure generic probe parameters
        section = ns.get_section('probes')
        defaultinterval = section.get_timedelta("default probe interval")
        defaultsplay = section.get_timedelta("default probe splay")
        # initialize each probe specified in the configuration
        for section in ns.find_sections('probe:/'):
            probepath = section.name[6:]
            try:
                probe = self.inventory.get_object(probepath)
                if probe is None:
                    raise Exception("probe is not enabled")
                interval = section.get_timedelta('probe interval', defaultinterval)
                splay = section.get_timedelta('probe splay', defaultsplay)
                # create a runner
                self.probes[probepath] = ProbeRunner(probe, interval, splay, self.deque)
            except ConfigureError:
                raise
            except Exception, e:
                logger.warning("ignoring probe %s: %s", probepath, str(e))

    def startService(self):
        logger.debug("starting probe scheduler")
        for name,probe in self.probes.items():
            splay = random.uniform(0.1, timedelta_to_seconds(probe.splay))
            logger.debug("initializing probe %s with splay %s", name, datetime.timedelta(seconds=splay))
            reactor.callLater(splay, probe.start)

    def stopService(self):
        logger.debug("stopping probe scheduler")
        for name,probe in self.probes.items():
            probe.stop()

class ProbeRunner(object):
    """
    """
    def __init__(self, probe, interval, splay, deque):
        self.probe = probe
        self.interval = interval
        self.splay = splay
        self.deque = deque
        self._lastexctype = None
        self._call = LoopingCall(self.call)

    def call(self):
        proberef = self.probe.ref
        try:
            # convert evaluation to messages if necessary
            result = self.probe.probe()
            if isinstance(result, Evaluation):
                logger.debug("probe %s evaluates %s", proberef, result)
                messages = [StatusMessage(proberef, result.health, result.summary, result.timestamp, result.detail)]
                if result.metrics is not None:
                    messages.append(MetricsMessage(proberef, result.metrics, result.timestamp))
                if result.events is not None:
                    messages.append(EventsMessage(proberef, result.events, result.timestamp))
                if result.metrics is not None:
                    messages.append(MetricsMessage(proberef, result.metrics, result.timestamp))
                if result.snapshot is not None:
                    messages.append(SnapshotMessage(proberef, result.snapshot, result.timestamp))
            # otherwise pass data along without conversion
            else:
                messages = result
            # broadcast messages to endpoints
            for message in messages:
                try:
                    self.deque.put_nowait(message)
                except Queue.Full:
                    logger.debug("agent queue is full, dropping message")
            # clear error flag
            if self._lastexctype is not None:
                self._lastexctype = None
        except Exception, e:
            if self._lastexctype is None or isinstance(e, self._lastexctype):
                logger.warning("probe %s generates error: %s", proberef, e)
                self._lastexctype = type(e)

    def start(self):
        logger.debug("starting probe %s with interval %s", self.probe.id, self.interval)
        self._call.start(timedelta_to_seconds(self.interval), True)

    def stop(self):
        if self._call.running:
            self._call.stop()
        logger.debug("stopped probe %s", self.probe.id)

def timedelta_to_seconds(td):
    """
    Convert a timedelta to seconds, represented as a float.
    """
    return (float(td.microseconds) + (float(td.seconds) + float(td.days) * 24.0 * 3600.0) * 10**6) / 10**6
