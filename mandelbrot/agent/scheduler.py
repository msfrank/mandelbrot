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
from twisted.internet.task import LoopingCall
from twisted.application.service import Service
from pesky.settings import ConfigureError
from mandelbrot.evaluation import Evaluation
from mandelbrot.message import StatusMessage, MetricsMessage
from mandelbrot.convert import timedelta2seconds
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.scheduler')

class SchedulerService(Service):
    """
    """
    def __init__(self):
        self.setName("SchedulerService")
        self.systems = dict()
        self.interval = None
        self.splay = None

    def configure(self, ns):
        # configure probe scheduling
        section = ns.get_section('agent')
        self.interval = section.get_timedelta("probe interval", datetime.timedelta(seconds=300))
        self.splay = section.get_timedelta("probe splay", datetime.timedelta(seconds=300))

    def schedule(self, system, queue):
        """
        """
        runners = dict()
        def _schedule(probes):
            for probe in probes:
                try:
                    ref = system.get_uri() + probe.get_path()
                    runner = ProbeRunner(ref, probe, self.interval, self.splay, queue)
                    runners[probe.get_path()] = runner
                    _schedule(map(lambda item: item[1], probe.iter_probes()))
                except Exception, e:
                    logger.warning("ignoring probe %s: %s", probe.get_path, str(e))
        logger.info("scheduling system %s", system.get_uri())
        _schedule(map(lambda item: item[1], system.iter_probes()))
        from twisted.internet import reactor
        for path,runner in runners.items():
            splay = random.uniform(0.1, timedelta2seconds(runner.splay))
            logger.debug("scheduling probe %s with splay %s", path, datetime.timedelta(seconds=splay))
            reactor.callLater(splay, runner.start)
        self.systems[system.get_uri()] = runners

    def unschedule(self, uri):
        """
        """
        runners = self.systems[uri]
        for path,runner in runners.items():
            runner.stop()
        del self.systems[uri]
        logger.info("unscheduled system %s", uri)

    def stopService(self):
        if len(self.systems) > 0:
            logger.debug("stopping scheduled systems")
            for uri in self.systems.keys():
                self.unschedule(uri)

class ProbeRunner(object):
    """
    """
    def __init__(self, proberef, probe, interval, splay, queue):
        self.proberef = proberef
        self.probe = probe
        self.interval = interval
        self.splay = splay
        self.queue = queue
        self._lastexctype = None
        self._call = LoopingCall(self.call)

    def call(self):
        try:
            # invoke probe and parse evaluation
            evaluation = self.probe.probe()
            if not isinstance(evaluation, Evaluation):
                raise TypeError("probe returns unknown type %s" % evaluation.__class__.__name__)
            logger.debug("probe %s evaluates %s", self.proberef, evaluation)
            messages = list()
            if evaluation.health is not None:
                health = evaluation.health
                timestamp = health.timestamp if health.timestamp is not None else evaluation.timestamp
                messages.append(StatusMessage(self.proberef, health.health, health.summary, timestamp))
            if evaluation.metrics is not None:
                metrics = evaluation.metrics
                timestamp = metrics.timestamp if metrics.timestamp is not None else evaluation.timestamp
                messages.append(MetricsMessage(self.proberef, metrics.metrics, timestamp))
            # send messages to endpoint
            for message in messages:
                try:
                    self.queue.put_nowait(message)
                except Queue.Full:
                    logger.debug("agent queue is full, dropping message")
            # clear error flag
            if self._lastexctype is not None:
                self._lastexctype = None
        except Exception, e:
            if self._lastexctype is None or isinstance(e, self._lastexctype):
                logger.warning("probe %s generates error: %s", self.proberef, e)
                self._lastexctype = type(e)

    def start(self):
        logger.debug("starting probe %s with interval %s", self.proberef, self.interval)
        self._call.start(timedelta2seconds(self.interval), True)

    def stop(self):
        if self._call.running:
            self._call.stop()
        logger.debug("stopped probe %s", self.proberef)
