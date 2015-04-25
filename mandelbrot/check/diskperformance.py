import os
import datetime
import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class DiskPerformance(Check):
    """
    Check system disk performance.

    Parameters:
    disk device              = PATH: path
    read failed threshold    = USAGE: int
    read degraded threshold  = USAGE: int
    write failed threshold   = USAGE: int
    write degraded threshold = USAGE: int
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def init(self):
        self.device = self.ns.get_str_or_default(cifparser.ROOT_PATH, "disk device")
        self.readdegraded = self.ns.get_int_or_default(cifparser.ROOT_PATH, "read degraded threshold")
        self.readfailed = self.ns.get_int_or_default(cifparser.ROOT_PATH, "read failed threshold")
        self.writedegraded = self.ns.get_int_or_default(cifparser.ROOT_PATH, "write degraded threshold")
        self.writefailed = self.ns.get_int_or_default(cifparser.ROOT_PATH, "write failed threshold")

    def execute(self):
        evaluation = Evaluation()
        evaluation.set_health(HEALTHY)
        if self.device is not None:
            disk = psutil.disk_io_counters(perdisk=True)[self.device]
        else:
            disk = psutil.disk_io_counters(perdisk=False)
        reads = disk.read_count
        writes = disk.write_count
        if self.device is not None:
            evaluation.set_summary("%i reads, %i writes on %s" % (reads,writes,self.device))
        else:
            evaluation.set_summary("%i reads, %i writes across all devices" % (reads,writes))
        if self.readdegraded is not None and reads > self.readdegraded:
            evaluation.set_health(DEGRADED)
        if self.writedegraded is not None and writes > self.writedegraded:
            evaluation.set_health(DEGRADED)
        if self.readfailed is not None and reads > self.readfailed:
            evaluation.set_health(FAILED)
        if self.writefailed is not None and writes > self.writefailed:
            evaluation.set_health(FAILED)
        return evaluation
