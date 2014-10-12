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

import os, datetime
from pesky.settings import ConfigureError
from twisted.application.service import Service
from mandelbrot.agent.systemfile import parse_systemdir, parse_systemfile
from mandelbrot.agent.state import StateDatabase
from mandelbrot.policy import Policy
from mandelbrot.metric import MetricSource
from mandelbrot.registration import SystemRegistration
from mandelbrot.endpoints import ResourceNotFound, ResourceConflict, RetryLater
from mandelbrot.convert import timedelta2seconds
from mandelbrot.defaults import defaults
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.registry')

class RegistryService(Service):
    """
    Manages the system inventory.
    """
    def __init__(self, plugins, scheduler, endpoint):
        self.setName("RegistryService")
        self.plugins = plugins
        self.scheduler = scheduler
        self.endpoint = endpoint
        self.state = None
        self.policy = None
        self.known = dict()
        self.registered = dict()
        self.failed = dict()
        self.retiring = dict()

    def configure(self, ns):
        section = ns.get_section('agent')
        # configure registration params
        self.maxattempts = section.get_int("max registration attempts", None)
        self.attemptdelay = timedelta2seconds(section.get_timedelta("registration attempt delay", datetime.timedelta(minutes=5)))
        # configure default probe policy
        joining_timeout = section.get_timedelta("joining timeout", datetime.timedelta(minutes=10))
        probe_timeout = section.get_timedelta("probe timeout", datetime.timedelta(minutes=10))
        alert_timeout = section.get_timedelta("alert timeout", datetime.timedelta(minutes=10))
        leaving_timeout = section.get_timedelta("leaving timeout", datetime.timedelta(days=1))
        notifications = section.get_list("notifications", None)
        self.default_policy = Policy(joining_timeout, probe_timeout, alert_timeout, leaving_timeout, notifications)
        # configure the state db
        path = section.get_path("state directory", os.path.join(defaults.get("LOCALSTATE_DIR"), "agent"))
        self.state = StateDatabase(path)
        # parse systems in system directory
        path = section.get_path("system directory", os.path.join(defaults.get("LOCALSTATE_DIR"), "systems"))
        logger.info("reading systems from %s", path)
        systemfiles = parse_systemdir(path)
        for systemfile in systemfiles:
            logger.debug("parsing system %s:%i", systemfile.path, systemfile.stream)
            systemspec = parse_systemfile(systemfile)
            system = self.make_system(systemspec)
            logger.info("parsed system %s", system.get_uri())
            self.known[system.get_uri()] = system

    def make_system(self, systemspec):
        """
        Given a system specification, instantiate the system and all
        of its probes, and return the system.
        """
        system = self.plugins.newinstance('io.mandelbrot.system', systemspec.systemtype)
        system_policy = self.default_policy.parse(systemspec.policy)
        system.configure(systemspec.systemtype, systemspec.settings, systemspec.metadata, system_policy)
        # initialize each probe specified in the configuration
        def make_probe(probes, parent):
            for probename,probespec in probes.items():
                try:
                    probe = self.plugins.newinstance('io.mandelbrot.probe', probespec.probetype)
                    probe_policy = system_policy.parse(probespec.policy)
                    probe.configure(probespec.path, probespec.probetype, probespec.settings, probespec.metadata, probe_policy)
                    parent.set_probe(probename, probe)
                    for name,metric in probe.iter_metrics():
                        source = MetricSource(probespec.path, name)
                        system.set_metric(source, metric)
                    make_probe(probespec.probes, probe)
                    logger.debug("configured probe %s", probespec.path)
                except ConfigureError, e:
                    raise
                except Exception, e:
                    logger.warning("failed to instantiate probe: %s", str(e))
        make_probe(systemspec.probes, system)
        logger.debug("configured system %s", system.get_uri())
        return system

    def on_registered(self, uri):
        logger.debug("registered system %s", uri)
        system = self.known.pop(uri)
        self.scheduler.schedule(system, self.endpoint.get_queue())
        self.registered[uri] = system

    def on_retry(self, failure, uri, registration, attemptsleft):
        if isinstance(failure.value, ResourceNotFound):
            logger.debug("attempting to register new system %s", uri)
            defer = self.endpoint.register(uri, registration)
        else:
            logger.debug("attempting to update existing system %s", uri)
            defer = self.endpoint.update(uri, registration)
        defer.addCallback(self.on_registered)
        defer.addErrback(self.on_failure, uri, registration, attemptsleft)

    def on_failure(self, failure, uri, registration, attemptsleft):
        from twisted.internet import reactor
        if attemptsleft == 0:
            logger.info("gave up registering system %s after failing %i times", uri, self.maxattempts)
        elif isinstance(failure.value, ResourceNotFound) or isinstance(failure.value, ResourceConflict):
            reactor.callLater(0, self.on_retry, failure, uri, registration, attemptsleft - 1)
        elif isinstance(failure.value, RetryLater):
            logger.info("retrying registering system %s in %i seconds", uri, self.attemptdelay)
            reactor.callLater(self.attemptdelay, self.on_retry, failure, uri, registration, attemptsleft - 1)
        else:
            self.failed[uri] = self.known.pop(uri)
            logger.error("gave up registering system %s after fatal error: %s", uri, failure.getErrorMessage())

    def register_system(self, uri, system):
        logger.debug("attempting to register new system %s", uri)
        registration = SystemRegistration(system)
        defer = self.endpoint.register(uri, registration)
        defer.addCallback(self.on_registered)
        defer.addErrback(self.on_failure, uri, registration, self.maxattempts)

    def startService(self):
        """
        """
        Service.startService(self)
        from twisted.internet import reactor
        logger.debug("performing initial registration")
        for uri,system in self.known.items():
            self.register_system(uri, system)

    def stopService(self):
        """
        """
        Service.stopService(self)
