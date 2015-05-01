import time
import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class NetPerformance(Check):
    """
    Check system network performance.

    Parameters:
    net device                       = DEVICE: str
    tx throughput failed threshold   = USAGE: int
    tx throughput degraded threshold = USAGE: int
    rx throughput failed threshold   = USAGE: int
    rx throughput degraded threshold = USAGE: int
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def _net_io_counters(self):
        if self.device is not None:
            return psutil.net_io_counters(pernic=True)[self.device]
        return psutil.net_io_counters(pernic=False)

    def init(self):
        self.device = self.ns.get_str_or_default(cifparser.ROOT_PATH, "net device")
        self.tx_thru_degraded = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "tx throughput degraded threshold")
        self.tx_thru_failed = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "tx throughput failed threshold")
        self.rx_thru_degraded = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "rx throughput degraded threshold")
        self.rx_thru_failed = self.ns.get_throughput_or_default(cifparser.ROOT_PATH,
            "rx throughput failed threshold")
        context = self._net_io_counters()._asdict()
        context['timestamp'] = time.time()
        return context

    def execute(self, evaluation, context):
        counters = self._net_io_counters()._asdict()
        timestamp = time.time()
        duration = timestamp - context['timestamp']
        bytes_sent_s = (counters['bytes_sent'] - context['bytes_sent']) / duration
        bytes_recv_s = (counters['bytes_recv'] - context['bytes_recv']) / duration
        packets_sent_s = (counters['packets_sent'] - context['packets_sent']) / duration
        packets_recv_s = (counters['packets_recv'] - context['packets_recv']) / duration
        errin_s = (counters['errin'] - context['errin']) / duration
        errout_s = (counters['errout'] - context['errout']) / duration
        dropin_s = (counters['dropin'] - context['dropin']) / duration
        dropout_s = (counters['dropout'] - context['dropout']) / duration
        context.update(counters, timestamp=timestamp)
        if self.device is not None:
            evaluation.set_summary(
                "%.1f M/s Tx (%.1f packets/s), %.1f M/s Rx (%.1f packets/s) on %s" % (
                bytes_sent_s / 1048576, packets_sent_s, bytes_recv_s / 1048576, packets_recv_s,
                self.device))
        else:
            evaluation.set_summary(
                "%.1f M/s Tx (%.1f packets/s), %.1f M/s Rx (%.1f packets/s) across all devices" % (
                    bytes_sent_s / 1048576, packets_sent_s, bytes_recv_s / 1048576, packets_recv_s))
        if self.tx_thru_failed is not None and bytes_sent_s > self.tx_thru_failed:
            evaluation.set_health(FAILED)
        elif self.rx_thru_failed is not None and bytes_recv_s > self.rx_thru_failed:
            evaluation.set_health(FAILED)
        elif self.tx_thru_degraded is not None and bytes_sent_s > self.tx_thru_degraded:
            evaluation.set_health(DEGRADED)
        elif self.rx_thru_degraded is not None and bytes_recv_s > self.rx_thru_degraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
