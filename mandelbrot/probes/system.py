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
from datetime import timedelta
from mandelbrot.probes import ScalarProbe
from mandelbrot.metric import Metric, SourceType, MetricUnit
from mandelbrot.table import size2string

class SystemLoad(ScalarProbe):
    """
    Check system load.

    Parameters:

    degraded threshold  = LOAD1: float, LOAD5: float, LOAD15: float
    failed threshold    = LOAD1: float, LOAD5: float, LOAD15: float
    divide per cpu      = PERCPU: boolean = false
    """
    def configure(self, path, probetype, settings, metadata, policy):
        self.loadfailed = settings.get_args("failed threshold", float, float, float,
                names=('LOAD1','LOAD5','LOAD15'), minimum=3, maximum=3)
        self.loaddegraded = settings.get_args("degraded threshold", float, float, float,
                names=('LOAD1','LOAD5','LOAD15'), minimum=3, maximum=3)
        self.percpu = settings.get_bool("divide per cpu", False)
        metrics = dict()
        metrics['load1'] = Metric(SourceType.GAUGE, MetricUnit.UNITS)
        metrics['load5'] = Metric(SourceType.GAUGE, MetricUnit.UNITS)
        metrics['load15'] = Metric(SourceType.GAUGE, MetricUnit.UNITS)
        ScalarProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

    def probe(self):
        load1, load5, load15 = os.getloadavg()
        ncores = psutil.cpu_count()
        summary = "load average is %.1f %.1f %.1f, detected %i cores" % (load1,load5,load15,ncores)
        metrics = dict(load1=load1, load5=load5, load15=load15)
        if self.percpu == True:
            load1 = load1 / float(ncores)
            load5 = load5 / float(ncores)
            load15 = load15 / float(ncores)
        if self.loadfailed is not None:
            fail1, fail5, fail15 = self.loadfailed
            if load1 > fail1 or load5 > fail5 or load15 > fail15:
                return self.failed(summary, metrics)
        if self.loaddegraded is not None:
            degr1, degr5, degr15 = self.loaddegraded
            if load1 > degr1 or load5 > degr5 or load15 > degr15:
                return self.degraded(summary, metrics)
        return self.healthy(summary, metrics)

class SystemCPU(ScalarProbe):
    """
    Check system CPU utilization.

    Parameters:
    user failed threshold     = USER: percent
    user degraded threshold   = USER: percent
    system failed threshold   = SYSTEM: percent
    system degraded threshold = SYSTEM: percent
    iowait failed threshold   = IOWAIT: percent
    iowait degraded threshold = IOWAIT: percent
    extended summary          = EXTENDED: bool = false
    """
    def __init__(self):
        ScalarProbe.__init__(self)
        # throw away the first value
        psutil.cpu_times_percent()

    def configure(self, path, probetype, settings, metadata, policy):
        self.userfailed = settings.get_percent("user failed threshold", None)
        self.userdegraded = settings.get_percent("user degraded threshold", None)
        self.systemfailed = settings.get_percent("system failed threshold", None)
        self.systemdegraded = settings.get_percent("system degraded threshold", None)
        self.iowaitfailed = settings.get_percent("iowait failed threshold", None)
        self.iowaitdegraded = settings.get_percent("iowait degraded threshold", None)
        self.extended = settings.get_bool("extended summary", False)
        metrics = dict()
        ScalarProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

    def probe(self):
        times = psutil.cpu_times_percent()
        items = sorted(times._asdict().items())
        if self.extended == False:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items if v != 0.0])
        else:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items])
        summary = "CPU utilization is " + showvals
        if self.userfailed is not None and times.user > self.userfailed:
            return self.failed(summary)
        if self.systemfailed is not None and times.system > self.systemfailed:
            return self.failed(summary)
        if self.iowaitfailed is not None and times.iowait > self.iowaitfailed:
            return self.failed(summary)
        if self.userdegraded is not None and times.user > self.userdegraded:
            return self.degraded(summary)
        if self.systemdegraded is not None and times.system > self.systemdegraded:
            return self.degraded(summary)
        if self.iowaitdegraded is not None and times.iowait > self.iowaitdegraded:
            return self.degraded(summary)
        return self.healthy(summary)

class SystemMemory(ScalarProbe):
    """
    Check system memory utilization.

    Parameters:
    memory failed threshold   = USAGE: size
    memory degraded threshold = USAGE: size
    swap failed threshold     = USAGE: size
    swap degraded threshold   = USAGE: size
    """
    def configure(self, path, probetype, settings, metadata, policy):
        self.memoryfailed = settings.get_size("memory failed threshold", None)
        self.memorydegraded = settings.get_size("memory degraded threshold", None)
        self.swapfailed = settings.get_size("swap failed threshold", None)
        self.swapdegraded = settings.get_size("swap degraded threshold", None)
        metrics = dict()
        ScalarProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

    def probe(self):
        memory = psutil.virtual_memory()
        memused = memory.percent
        memtotal = size2string(memory.total)
        swap = psutil.swap_memory()
        swapused = swap.percent
        swaptotal = size2string(swap.total)
        summary = "%.1f%% used of %s of physical memory; %.1f%% used of %s of swap" % (memused,memtotal,swapused,swaptotal)
        if self.memoryfailed is not None and memory.used > self.memoryfailed:
            return self.failed(summary)
        if self.swapfailed is not None and swap.used > self.swapfailed:
            return self.failed(summary)
        if self.memorydegraded is not None and memory.used > self.memorydegraded:
            return self.degraded(summary)
        if self.swapdegraded is not None and swap.used > self.swapdegraded:
            return self.degraded(summary)
        return self.healthy(summary)

class SystemDiskUsage(ScalarProbe):
    """
    Check system disk utilization.

    Parameters:
    disk partition          = PATH: path = /
    disk failed threshold   = USAGE: size
    disk degraded threshold = USAGE: size
    """
    def configure(self, path, probetype, settings, metadata, policy):
        self.partition = settings.get_path("disk partition", "/")
        self.diskfailed = settings.get_size("disk failed threshold", None)
        self.diskdegraded = settings.get_size("disk degraded threshold", None)
        metrics = dict()
        ScalarProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

    def probe(self):
        disk = psutil.disk_usage(self.partition)
        diskused = disk.percent
        disktotal = size2string(disk.total)
        summary = "%.1f%% used of %s on %s" % (diskused,disktotal,self.partition)
        if self.diskfailed is not None and disk.used > self.diskfailed:
            return self.failed(summary)
        if self.diskdegraded is not None and disk.used > self.diskdegraded:
            return self.degraded(summary)
        return self.healthy(summary)

class SystemDiskPerformance(ScalarProbe):
    """
    Check system disk performance.

    Parameters:
    disk device              = PATH: path
    read failed threshold    = USAGE: int
    read degraded threshold  = USAGE: int
    write failed threshold   = USAGE: int
    write degraded threshold = USAGE: int
    """
    def configure(self, path, probetype, settings, metadata, policy):
        self.device = settings.get_path("disk device", None)
        self.readfailed = settings.get_int("read failed threshold", None)
        self.readdegraded = settings.get_int("read degraded threshold", None)
        self.writefailed = settings.get_int("write failed threshold", None)
        self.writedegraded = settings.get_int("write degraded threshold", None)
        metrics = dict()
        ScalarProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

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
        if self.readfailed is not None and reads > self.readfailed:
            return self.failed(summary)
        if self.writefailed is not None and writes > self.writefailed:
            return self.failed(summary)
        if self.readdegraded is not None and reads > self.readdegraded:
            return self.degraded(summary)
        if self.writedegraded is not None and writes > self.writedegraded:
            return self.degraded(summary)
        return self.healthy(summary)

class SystemNetPerformance(ScalarProbe):
    """
    Check system network performance.

    Parameters:
    net device              = DEVICE: str
    send failed threshold   = USAGE: int
    send degraded threshold = USAGE: int
    recv failed threshold   = USAGE: int
    recv degraded threshold = USAGE: int
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemNetPerformance"

    def configure(self, path, probetype, settings, metadata, policy):
        self.device = settings.get_str("net device", None)
        self.sendfailed = settings.get_int("send failed threshold", None)
        self.senddegraded = settings.get_int("send degraded threshold", None)
        self.recvfailed = settings.get_int("recv failed threshold", None)
        self.recvdegraded = settings.get_int("recv degraded threshold", None)
        metrics = dict()
        ScalarProbe.configure(self, path, probetype, settings, metadata, policy, metrics)

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
        if self.sendfailed is not None and tx > self.sendfailed:
            return self.failed(summary)
        if self.recvfailed is not None and rx > self.recvfailed:
            return self.failed(summary)
        if self.senddegraded is not None and tx > self.senddegraded:
            return self.degraded(summary)
        if self.recvdegraded is not None and rx > self.recvdegraded:
            return self.degraded(summary)
        return self.healthy(summary)

