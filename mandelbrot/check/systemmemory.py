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
        evaluation.set_metric('memavail', memavail)
        evaluation.set_metric('memused', memused)
        evaluation.set_metric('memtotal', memtotal)
        evaluation.set_metric('swapavail', swapavail)
        evaluation.set_metric('swapused', swapused)
        evaluation.set_metric('swaptotal', swaptotal)
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
