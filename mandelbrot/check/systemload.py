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
