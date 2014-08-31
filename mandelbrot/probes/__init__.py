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

from zope.interface import Interface, implements
from mandelbrot.behavior import *
from mandelbrot.evaluation import Evaluation, Health, Metrics

class IProbe(Interface):

    def configure(self, path, probetype, settings, metadata, policy):
        ""

    def get_name(self):
        ""

    def get_path(self):
        ""

    def get_type(self):
        ""

    def get_metadata(self):
        ""

    def get_policy(self):
        ""

    def get_behavior(self):
        ""

    def get_probe(self, name):
        ""

    def set_probe(self, name, probe):
        ""

    def iter_probes(self):
        ""

    def is_synthetic(self):
        ""

    def probe(self):
        ""

class Probe(object):
    """
    """
    def __init__(self):
        self._path = None
        self._probetype = None
        self._metadata = None
        self._policy = None
        self._probes = dict()

    def configure(self, path, probetype, metadata, policy):
        self._path = path
        self._probetype = probetype
        self._metadata = metadata
        self._policy = policy

    def get_name(self):
        return self._path.split('/')[-1]

    def get_path(self):
        return self._path

    def get_type(self):
        return self._probetype

    def get_metadata(self):
        return self._metadata

    def get_policy(self):
        return self._policy

    def get_probe(self, name):
        return self._probes[name]

    def set_probe(self, name, probe):
        self._probes[name] = probe

    def iter_probes(self):
        return self._probes.iteritems()

class ScalarProbe(Probe):
    """
    """
    def configure(self, path, probetype, settings, metadata, policy):
        Probe.configure(self, path, probetype, metadata, policy)

    def get_behavior(self):
        return ScalarBehavior(0, 0)

    def is_synthetic(self):
        return False

    def evaluate(self, health, summary=None, metrics=None, timestamp=None):
        if metrics is not None:
            return Evaluation(Health(health, summary), Metrics(metrics), timestamp=timestamp)
        return Evaluation(Health(health, summary), timestamp=timestamp)

    def healthy(self, summary=None, metrics=None, timestamp=None):
        return self.evaluate(Health.HEALTHY, summary, metrics, timestamp)

    def degraded(self, summary=None, metrics=None, timestamp=None):
        return self.evaluate(Health.DEGRADED, summary, metrics, timestamp)

    def failed(self, summary=None, metrics=None, timestamp=None):
        return self.evaluate(Health.FAILED, summary, metrics, timestamp)

    def unknown(self, summary=None, metrics=None, timestamp=None):
        return self.evaluate(Health.UNKNOWN, summary, metrics, timestamp)

class AggregateProbe(Probe):
    """
    """
    def configure(self, path, probetype, settings, metadata, policy):
        Probe.configure(self, path, probetype, metadata, policy)

    def get_behavior(self):
        return AggregateBehavior(0, 0)

    def is_synthetic(self):
        return True

class MetricsProbe(Probe):
    """
    """
    def configure(self, path, probetype, settings, metadata, policy):
        Probe.configure(self, path, probetype, metadata, policy)

    def get_behavior(self):
        return MetricsBehavior(0, 0)

    def is_synthetic(self):
        return False

    def evaluate(self, metrics, timestamp=None):
        return Evaluation(None, Metrics(metrics), timestamp=timestamp)

