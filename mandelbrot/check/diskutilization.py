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

class DiskUtilization(Check):
    """
    Check system disk utilization.

    Parameters:
    mount point             = PATH: path = /
    disk degraded threshold = USAGE: size
    disk failed threshold   = USAGE: size
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarCheck"

    def get_behavior(self):
        return {}

    def init(self):
        self.mountpoint = self.ns.get_str_or_default(cifparser.ROOT_PATH, "mount point", "/")
        self.diskdegraded = self.ns.get_size_or_default(cifparser.ROOT_PATH, "disk degraded threshold")
        self.diskfailed = self.ns.get_size_or_default(cifparser.ROOT_PATH, "disk failed threshold")
        return None

    def execute(self, evaluation, context):
        disk = psutil.disk_usage(self.mountpoint)
        diskused = disk.percent
        disktotal = disk.total
        diskavail = disk.total - disk.used
        evaluation.set_summary("%.1f%% used of %s on %s" % (
            diskused, disktotal, self.mountpoint))
        if self.diskfailed is not None and disk.used > self.diskfailed:
            evaluation.set_health(FAILED)
        elif self.diskdegraded is not None and disk.used > self.diskdegraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
