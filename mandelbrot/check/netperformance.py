import psutil
import cifparser

from mandelbrot.check import Check
from mandelbrot.model.evaluation import *

class NetPerformance(Check):
    """
    Check system network performance.

    Parameters:
    net device            = DEVICE: str
    tx failed threshold   = USAGE: int
    tx degraded threshold = USAGE: int
    rx failed threshold   = USAGE: int
    rx degraded threshold = USAGE: int
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def init(self):
        self.device = self.ns.get_str_or_default(cifparser.ROOT_PATH, "net device")
        self.senddegraded = self.ns.get_int_or_default(cifparser.ROOT_PATH, "tx degraded threshold")
        self.sendfailed = self.ns.get_int_or_default(cifparser.ROOT_PATH, "tx failed threshold")
        self.recvdegraded = self.ns.get_int_or_default(cifparser.ROOT_PATH, "rx degraded threshold")
        self.recvfailed = self.ns.get_int_or_default(cifparser.ROOT_PATH, "rx failed threshold")
        return None

    def execute(self, evaluation, context):
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
            evaluation.set_summary("%i packets sent, %i packets received on %s" % (tx,rx,self.device))
        else:
            evaluation.set_summary("%i packets sent, %i packets received across all devices" % (tx,rx))
        if self.sendfailed is not None and tx > self.sendfailed:
            evaluation.set_health(FAILED)
        elif self.recvfailed is not None and rx > self.recvfailed:
            evaluation.set_health(FAILED)
        elif self.senddegraded is not None and tx > self.senddegraded:
            evaluation.set_health(DEGRADED)
        elif self.recvdegraded is not None and rx > self.recvdegraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
