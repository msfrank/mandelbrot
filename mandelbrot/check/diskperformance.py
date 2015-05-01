import time
import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class DiskPerformance(Check):
    """
    Check system disk performance.

    Parameters:
    disk device                   = PATH: path
    read rate failed threshold    = USAGE: throughput
    read rate degraded threshold  = USAGE: throughput
    write rate failed threshold   = USAGE: throughput
    write rate degraded threshold = USAGE: throughput
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def _disk_io_counters(self):
        if self.device is not None:
            return psutil.disk_io_counters(perdisk=True)[self.device]
        return psutil.disk_io_counters(perdisk=False)

    def init(self):
        self.device = self.ns.get_str_or_default(cifparser.ROOT_PATH, "disk device")
        self.read_rate_degraded = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "read rate degraded threshold")
        self.read_rate_failed = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "read rate failed threshold")
        self.write_rate_degraded = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "write rate degraded threshold")
        self.write_rate_failed = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "write rate failed threshold")
        context = self._disk_io_counters()._asdict()
        context['timestamp'] = time.time()
        return context

    def execute(self, evaluation, context):
        counters = self._disk_io_counters()._asdict()
        timestamp = time.time()
        duration = timestamp - context['timestamp']
        read_count_s = (counters['read_count'] - context['read_count']) / duration
        write_count_s = (counters['write_count'] - context['write_count']) / duration
        read_bytes_s = (counters['read_bytes'] - context['read_bytes']) / duration
        write_bytes_s = (counters['write_bytes'] - context['write_bytes']) / duration
        read_pct = ((counters['read_time'] - context['read_time']) * 100.0) / duration
        write_pct = ((counters['write_time'] - context['write_time']) * 100.0) / duration
        context.update(counters, timestamp=timestamp)
        if self.device is not None:
            evaluation.set_summary(
                "%.1f%% reads, %i reads/s (%.1f M/s), %.1f%% writes, %i writes/s (%.1f M/s) on %s" % (
                read_pct, read_count_s, read_bytes_s / 1048576, write_pct, write_count_s, write_bytes_s / 1048576,
                self.device))
        else:
            evaluation.set_summary(
                "%.1f%% reads, %i reads/s (%.1f M/s), %.1f%% writes, %i writes/s (%.1f M/s) across all devices" % (
                    read_pct, read_count_s, read_bytes_s / 1048576, write_pct, write_count_s, write_bytes_s / 1048576))
        if self.read_rate_failed is not None and read_count_s > self.read_rate_failed:
            evaluation.set_health(FAILED)
        elif self.write_rate_failed is not None and write_count_s > self.write_rate_failed:
            evaluation.set_health(FAILED)
        elif self.read_rate_degraded is not None and read_count_s > self.read_rate_degraded:
            evaluation.set_health(DEGRADED)
        elif self.write_rate_degraded is not None and write_count_s > self.write_rate_degraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
