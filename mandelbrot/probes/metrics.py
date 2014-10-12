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

import os, psutil
from datetime import timedelta
from mandelbrot.probes import MetricsProbe
from mandelbrot.behavior import MetricsBehavior
from mandelbrot.metric import Metric, SourceType, MetricUnit
from mandelbrot.table import size2string

class MetricsEvaluation(MetricsProbe):
    """
    Evaluate metrics.

    Parameters:

    failed threshold    = EXPRESSION: str
    """
    def configure(self, path, probetype, settings, metadata, policy):
        self.exprfailed = settings.get_str("failed threshold", None)
        metrics = dict()
        MetricsProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

    def get_behavior(self):
        return MetricsBehavior(self.exprfailed, 0, 0)

    def is_synthetic(self):
        return True

class MetricsProxy(MetricsProbe):
    """
    Evaluate metrics.

    Parameters:

    failed threshold    = EXPRESSION: str
    """
    def configure(self, path, probetype, settings, metadata, policy):
        self.exprfailed = settings.get_str("failed threshold", None)
        metrics = dict()
        MetricsProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

    def get_behavior(self):
        return MetricsBehavior(self.exprfailed, 0, 0)

    def is_synthetic(self):
        return False

    def evaluate(self, metrics, timestamp=None):
        return Evaluation(None, Metrics(metrics), timestamp=timestamp)
