import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class SystemMemory(Check):
    """
    Check system memory utilization.

    Parameters:
    memory failed threshold   = USAGE: size
    memory degraded threshold = USAGE: size
    swap failed threshold     = USAGE: size
    swap degraded threshold   = USAGE: size
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarCheck"

    def get_behavior(self):
        return {}

    def init(self):
        self.memoryfailed = self.ns.get_size_or_default(cifparser.ROOT_PATH, "memory failed threshold")
        self.memorydegraded = self.ns.get_size_or_default(cifparser.ROOT_PATH, "memory degraded threshold")
        self.swapfailed = self.ns.get_size_or_default(cifparser.ROOT_PATH, "swap failed threshold")
        self.swapdegraded = self.ns.get_size_or_default(cifparser.ROOT_PATH, "swap degraded threshold")
        return None

    def execute(self, evaluation, context):
        memory = psutil.virtual_memory()
        memavail = memory.available
        memused = memory.percent
        memtotal = memory.total
        swap = psutil.swap_memory()
        swapavail = swap.total - swap.used
        swapused = swap.percent
        swaptotal = swap.total
        evaluation.set_summary("%.1f%% used of %s of physical memory; %.1f%% used of %s of swap" % (
            memused, str(memtotal), swapused, str(swaptotal)))
        if self.memoryfailed is not None and memory.used > self.memoryfailed:
            evaluation.set_health(FAILED)
        elif self.swapfailed is not None and swap.used > self.swapfailed:
            evaluation.set_health(FAILED)
        elif self.memorydegraded is not None and memory.used > self.memorydegraded:
            evaluation.set_health(DEGRADED)
        elif self.swapdegraded is not None and swap.used > self.swapdegraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
