# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
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

import os
import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class SystemLoad(Check):
    """
    Check system load.
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarCheck"

    def get_behavior(self):
        return {}

    def init(self):
        self.failed_1min = self.ns.get_float_or_default(cifparser.ROOT_PATH, "1min failed threshold")
        self.degraded_1min = self.ns.get_float_or_default(cifparser.ROOT_PATH, "1min degraded threshold")
        self.failed_5min = self.ns.get_float_or_default(cifparser.ROOT_PATH, "5min failed threshold")
        self.degraded_5min = self.ns.get_float_or_default(cifparser.ROOT_PATH, "5min degraded threshold")
        self.failed_15min = self.ns.get_float_or_default(cifparser.ROOT_PATH, "15min failed threshold")
        self.degraded_15min = self.ns.get_float_or_default(cifparser.ROOT_PATH, "15min degraded threshold")
        self.per_cpu = self.ns.get_bool_or_default(cifparser.ROOT_PATH, "divide per cpu", False)
        self.cache_cpu_count = self.ns.get_bool_or_default(cifparser.ROOT_PATH, "cache cpu count", False)
        if self.cache_cpu_count:
            self.cpu_count = psutil.cpu_count()
        else:
            self.cpu_count = None
        return None

    def execute(self, evaluation, context):
        load1, load5, load15 = os.getloadavg()
        ncores = self.cpu_count if self.cache_cpu_count else psutil.cpu_count()
        evaluation.set_summary("load average is %.1f %.1f %.1f, detected %i cores" % (
            load1, load5, load15, ncores))
        if self.per_cpu == True:
            load1 = load1 / float(ncores)
            load5 = load5 / float(ncores)
            load15 = load15 / float(ncores)
        evaluation.set_metric('load1', load1)
        evaluation.set_metric('load5', load5)
        evaluation.set_metric('load15', load15)
        if self.failed_1min is not None and load1 > self.failed_1min:
            evaluation.set_health(FAILED)
        elif self.failed_5min is not None and load5 > self.failed_5min:
            evaluation.set_health(FAILED)
        elif self.failed_15min is not None and load15 > self.failed_15min:
            evaluation.set_health(FAILED)
        elif self.degraded_1min is not None and load1 > self.degraded_1min:
            evaluation.set_health(DEGRADED)
        elif self.degraded_5min is not None and load5 > self.degraded_5min:
            evaluation.set_health(DEGRADED)
        elif self.degraded_15min is not None and load15 > self.degraded_15min:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
