import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import *

MockNetIO = collections.namedtuple('MockNetIO', [ 'bytes_sent', "bytes_recv",
    "packets_sent", "packets_recv", "errin", "errout", "dropin", "dropout"])

class TestNetPerformance(unittest.TestCase):

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_healthy(self, time, net_io_counters):
        "NetPerformance check should return healthy evaluation when no thresholds are specified"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_tx_healthy(self, time, net_io_counters):
        "NetPerformance check should return healthy evaluation when tx throughput is not breaching threshold"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "tx throughput degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "tx throughput failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_tx_throughput_degraded(self, time, net_io_counters):
        "NetPerformance check should return degraded evaluation when tx throughput breaches degraded threshold"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=5000, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "tx throughput degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "tx throughput failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_tx_throughput_failed(self, time, net_io_counters):
        "NetPerformance check should return failed evaluation when tx throughput breaches failed threshold"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=10000, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "tx throughput degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "tx throughput failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), FAILED)

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_rx_healthy(self, time, net_io_counters):
        "NetPerformance check should return healthy evaluation when rx throughput is not breaching threshold"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "rx throughput degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "rx throughput failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_rx_throughput_degraded(self, time, net_io_counters):
        "NetPerformance check should return degraded evaluation when rx throughput breaches degraded threshold"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=0, bytes_recv=5000, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "rx throughput degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "rx throughput failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.net_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_NetPerformance_check_rx_throughput_failed(self, time, net_io_counters):
        "NetPerformance check should return failed evaluation when rx throughput breaches failed threshold"
        time.side_effect = [0.0, 100.0]
        net_io_counters.side_effect = [
            MockNetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            MockNetIO(bytes_sent=0, bytes_recv=10000, packets_sent=0, packets_recv=0,
                      errin=0, errout=0, dropin=0, dropout=0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "rx throughput degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "rx throughput failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.netperformance import NetPerformance
        check = NetPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), FAILED)
