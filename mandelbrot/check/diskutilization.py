import os
import datetime
import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class DiskUtilization(Check):
    """
    Check system disk utilization.

    Parameters:
    mount point             = PATH: path = /
    disk degraded threshold = USAGE: size
    disk failed threshold   = USAGE: size
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def init(self):
        self.mountpoint = self.ns.get_str_or_default(cifparser.ROOT_PATH, "mount point", "/")
        self.diskdegraded = self.ns.get_size_or_default(cifparser.ROOT_PATH, "disk degraded threshold")
        self.diskfailed = self.ns.get_size_or_default(cifparser.ROOT_PATH, "disk failed threshold")

    def execute(self):
        evaluation = Evaluation()
        evaluation.set_health(HEALTHY)
        disk = psutil.disk_usage(self.mountpoint)
        diskused = disk.percent
        disktotal = disk.total
        diskavail = disk.total - disk.used
        evaluation.set_summary("%.1f%% used of %s on %s" % (
            diskused, disktotal, self.mountpoint))
        if self.diskdegraded is not None and disk.used > self.diskdegraded:
            evaluation.set_health(DEGRADED)
        if self.diskfailed is not None and disk.used > self.diskfailed:
            evaluation.set_health(FAILED)
        return evaluation
