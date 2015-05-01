import time
import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class SystemCPU(Check):
    """
    Check system CPU utilization.

    Parameters:
    user failed threshold     = USER: percentage
    user degraded threshold   = USER: percentage
    system failed threshold   = SYSTEM: percentage
    system degraded threshold = SYSTEM: percentage
    iowait failed threshold   = IOWAIT: percentage
    iowait degraded threshold = IOWAIT: percentage
    idle failed threshold     = IDLE: percentage
    idle degraded threshold   = IDLE: percentage
    extended summary          = EXTENDED: bool = false
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def init(self):
        self.userfailed = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "user failed threshold")
        self.userdegraded = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "user degraded threshold")
        self.systemfailed = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "system failed threshold")
        self.systemdegraded = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "system degraded threshold")
        self.iowaitfailed = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "iowait failed threshold")
        self.iowaitdegraded = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "iowait degraded threshold")
        self.idlefailed = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "idle failed threshold")
        self.idledegraded = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "idle degraded threshold")
        self.extended = self.ns.get_bool_or_default(cifparser.ROOT_PATH, "extended summary", False)
        context = psutil.cpu_times()._asdict()
        context['timestamp'] = time.time()
        return context

    def execute(self, evaluation, context):
        times = psutil.cpu_times()._asdict()
        timestamp = time.time()
        duration = timestamp - context['timestamp']
        pct = {}
        for key,value in times.items():
            pct[key] = ((value - context[key]) / duration) * 100.0
        items = sorted(pct.items())
        context.update(times, timestamp=timestamp)
        if not self.extended:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items if v != 0.0])
        else:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items])
        evaluation.set_summary("CPU utilization is " + showvals)
        if self.userfailed is not None and pct['user'] / 100.0 > self.userfailed:
            evaluation.set_health(FAILED)
        elif self.systemfailed is not None and pct['system'] / 100.0 > self.systemfailed:
            evaluation.set_health(FAILED)
        elif self.iowaitfailed is not None and pct['iowait'] / 100.0 > self.iowaitfailed:
            evaluation.set_health(FAILED)
        elif self.idlefailed is not None and pct['idle'] / 100.0 > self.idlefailed:
            evaluation.set_health(FAILED)
        elif self.userdegraded is not None and pct['user'] / 100.0 > self.userdegraded:
            evaluation.set_health(DEGRADED)
        elif self.systemdegraded is not None and pct['system'] / 100.0 > self.systemdegraded:
            evaluation.set_health(DEGRADED)
        elif self.iowaitdegraded is not None and pct['iowait'] / 100.0 > self.iowaitdegraded:
            evaluation.set_health(DEGRADED)
        elif self.idledegraded is not None and pct['idle'] / 100.0 > self.idledegraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
