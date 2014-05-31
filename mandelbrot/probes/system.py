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
from mandelbrot.probes import Probe
from mandelbrot.evaluation import Evaluation, Health


class SystemLoad(Probe):
    """
    Check system load.

    Parameters:

    degraded threshold  = LOAD1: float, LOAD5: float, LOAD15: float
    failed threshold    = LOAD1: float, LOAD5: float, LOAD15: float
    divide per cpu      = PERCPU: boolean
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemLoad"

    def configure(self, section):
        self.failed = section.get_args("failed threshold", float, float, float,
                names=('LOAD1','LOAD5','LOAD15'), minimum=3, maximum=3)
        self.degraded = section.get_args("degraded threshold", float, float, float,
                names=('LOAD1','LOAD5','LOAD15'), minimum=3, maximum=3)
        self.percpu = section.get_bool("divide per cpu", False)
        Probe.configure(self, section)

    def probe(self):
        load1, load5, load15 = os.getloadavg()
        ncores = psutil.cpu_count()
        summary = "load average is %.1f %.1f %.1f, detected %i cores" % (load1,load5,load15,ncores)
        if self.percpu == True:
            load1 = load1 / float(ncores)
            load5 = load5 / float(ncores)
            load15 = load15 / float(ncores)
        if self.failed is not None:
            fail1, fail5, fail15 = self.failed
            if load1 > fail1 or load5 > fail5 or load15 > fail15:
                return Evaluation(Health.FAILED, summary)
        if self.degraded is not None:
            degr1, degr5, degr15 = self.degraded
            if load1 > degr1 or load5 > degr5 or load15 > degr15:
                return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemCPU(Probe):
    """
    Check system CPU utilization.

    Parameters:
    user failed threshold     = USER: percentage
    user degraded threshold   = USER: percentage
    system failed threshold   = SYSTEM: percentage
    system degraded threshold = SYSTEM: percentage
    iowait failed threshold   = IOWAIT: percentage
    iowait degraded threshold = IOWAIT: percentage
    """
    def __init__(self):
        Probe.__init__(self)
        # throw away the first value
        psutil.cpu_times_percent()

    def get_type(self):
        return "io.mandelbrot.probe.SystemCPU"

    def configure(self, section):
        self.userfailed = section.get_percentage("user failed threshold", None)
        self.userdegraded = section.get_percentage("user degraded threshold", None)
        self.systemfailed = section.get_percentage("system failed threshold", None)
        self.systemdegraded = section.get_percentage("system degraded threshold", None)
        self.iowaitfailed = section.get_percentage("iowait failed threshold", None)
        self.iowaitdegraded = section.get_percentage("iowait degraded threshold", None)
        self.extended = section.get_bool("extended summary", False)
        Probe.configure(self, section)

    def probe(self):
        times = psutil.cpu_times_percent()
        items = sorted(times._asdict().items())
        if self.extended == False:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items if v != 0.0])
        else:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items])
        summary = "CPU utilization is " + showvals
        if self.userfailed is not None and times.user > self.userfailed:
            return Evaluation(Health.FAILED, summary)
        if self.systemfailed is not None and times.system > self.systemfailed:
            return Evaluation(Health.FAILED, summary)
        if self.iowaitfailed is not None and times.iowait > self.iowaitfailed:
            return Evaluation(Health.FAILED, summary)
        if self.userdegraded is not None and times.user > self.userdegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.systemdegraded is not None and times.system > self.systemdegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.iowaitdegraded is not None and times.iowait > self.iowaitdegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemMemory(Probe):
    """
    Check system CPU utilization.

    Parameters:
    memory failed threshold   = MEMORY: size
    memory degraded threshold = MEMORY: size
    swap failed threshold     = SWAP: size
    swap degraded threshold   = SWAP: size
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemMemory"

    def configure(self, section):
        self.memoryfailed = section.get_size("memory failed threshold", None)
        self.memorydegraded = section.get_size("memory degraded threshold", None)
        self.swapfailed = section.get_size("swap failed threshold", None)
        self.swapdegraded = section.get_size("swap degraded threshold", None)
        Probe.configure(self, section)

    def _printsize(self, size):
        if size < 1024:
            return "%i bytes" % size
        if size < 1024 * 1024:
            return "%.1f kilobytes" % (float(size) / 1024.0)
        if size < 1024 * 1024 * 1024:
            return "%.1f megabytes" % (float(size) / (1024.0 * 1024.0))
        if size < 1024 * 1024 * 1024 * 1024:
            return "%.1f gigabytes" % (float(size) / (1024.0 * 1024.0 * 1024.0))
        if size < 1024 * 1024 * 1024 * 1024 * 1024:
            return "%.1f terabytes" % (float(size) / (1024.0 * 1024.0 * 1024.0 * 1024.0))

    def probe(self):
        memory = psutil.virtual_memory()
        memused = memory.percent
        memtotal = self._printsize(memory.total)
        swap = psutil.swap_memory()
        swapused = swap.percent
        swaptotal = self._printsize(swap.total)
        summary = "%.1f%% used of %s of physical memory; %.1f%% used of %s of swap" % (memused,memtotal,swapused,swaptotal)
        if self.memoryfailed is not None and memory.used > self.memoryfailed:
            return Evaluation(Health.FAILED, summary)
        if self.swapfailed is not None and swap.used > self.swapfailed:
            return Evaluation(Health.FAILED, summary)
        if self.memorydegraded is not None and memory.used > self.memorydegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.swapdegraded is not None and swap.used > self.swapdegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemDiskUsage(Probe):
    """
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemDiskUsage"

    def configure(self, section):
        self.partition = section.get_path("disk partition", "/")
        Probe.configure(self, section)

    def probe(self):
        disk = psutil.disk_usage(self.partition)
        diskused = disk.percent
        disktotal = disk.total
        summary = "%.1f%% used of %i bytes on %s" % (diskused,disktotal,self.partition)
        return Evaluation(Health.HEALTHY, summary)

class SystemDiskPerformance(Probe):
    """
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemDiskPerformance"

    def configure(self, section):
        self.device = section.get_path("disk device", None)
        Probe.configure(self, section)

    def probe(self):
        if self.device is not None:
            disk = psutil.disk_io_counters(perdisk=True)[self.device]
        else:
            disk = psutil.disk_io_counters(perdisk=False)
        reads = disk.read_count
        writes = disk.write_count
        if self.device is not None:
            summary = "%i reads, %i writes on %s" % (reads,writes,self.device)
        else:
            summary = "%i reads, %i writes across all devices" % (reads,writes)
        return Evaluation(Health.HEALTHY, summary)

class SystemNetPerformance(Probe):
    """
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemNetPerformance"

    def configure(self, section):
        self.device = section.get_path("net device", None)
        Probe.configure(self, section)

    def probe(self):
        if self.device is not None:
            net = psutil.net_io_counters(pernic=True)[self.device]
        else:
            net = psutil.net_io_counters(pernic=False)
        tx = net.packets_sent
        rx = net.packets_recv
        errin = net.errin
        errout = net.errout
        dropin = net.dropin
        dropout = net.dropout
        if self.device is not None:
            summary = "%i packets sent, %i packets received on %s" % (tx,rx,self.device)
        else:
            summary = "%i packets sent, %i packets received across all devices" % (tx,rx)
        return Evaluation(Health.HEALTHY, summary)

