import os
import datetime
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
        # has side effect of throwing away the first value
        psutil.cpu_times_percent()

    def execute(self):
        evaluation = Evaluation()
        evaluation.set_health(HEALTHY)
        times = psutil.cpu_times_percent()
        items = sorted(times._asdict().items())
        if not self.extended:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items if v != 0.0])
        else:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items])
        evaluation.set_summary("CPU utilization is " + showvals)
        if self.userdegraded is not None and times.user > self.userdegraded:
            evaluation.set_health(DEGRADED)
        if self.systemdegraded is not None and times.system > self.systemdegraded:
            evaluation.set_health(DEGRADED)
        if self.iowaitdegraded is not None and times.iowait > self.iowaitdegraded:
            evaluation.set_health(DEGRADED)
        if self.idledegraded is not None and times.idle < self.idledegraded:
            evaluation.set_health(DEGRADED)
        if self.userfailed is not None and times.user > self.userfailed:
            evaluation.set_health(FAILED)
        if self.systemfailed is not None and times.system > self.systemfailed:
            evaluation.set_health(FAILED)
        if self.iowaitfailed is not None and times.iowait > self.iowaitfailed:
            evaluation.set_health(FAILED)
        if self.idlefailed is not None and times.idle < self.idlefailed:
            evaluation.set_health(FAILED)
        return evaluation
