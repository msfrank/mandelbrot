import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import *

MockDiskIO = collections.namedtuple('MockDiskIO', ['read_count', 'write_count',
    'read_bytes', 'write_bytes', 'read_time', 'write_time'])

class TestDiskPerformance(unittest.TestCase):

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_healthy(self, time, disk_io_counters):
        "DiskPerformance check should return healthy evaluation when no thresholds are specified"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_healthy(self, time, disk_io_counters):
        "DiskPerformance check should return healthy evaluation when read rate is not breaching threshold"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "read rate degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "read rate failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_read_degraded(self, time, disk_io_counters):
        "DiskPerformance check should return degraded evaluation when read rate breaches degraded threshold"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=5000.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "read rate degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "read rate failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_read_failed(self, time, disk_io_counters):
        "DiskPerformance check should return failed evaluation when read rate breaches failed threshold"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=10000.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "read rate degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "read rate failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), FAILED)

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_write_rate_healthy(self, time, disk_io_counters):
        "DiskPerformance check should return healthy evaluation when write rate is not breaching threshold"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "write rate degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "write rate failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_write_rate_degraded(self, time, disk_io_counters):
        "DiskPerformance check should return degraded evaluation when write rate breaches degraded threshold"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=0.0, write_count=5000.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "write rate degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "write rate failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.disk_io_counters')
    @unittest.mock.patch('time.time')
    def test_execute_DiskPerformance_check_write_rate_failed(self, time, disk_io_counters):
        "DiskPerformance check should return failed evaluation when write rate breaches failed threshold"
        time.side_effect = [0.0, 100.0]
        disk_io_counters.side_effect = [
            MockDiskIO(read_count=0.0, write_count=0.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            MockDiskIO(read_count=0.0, write_count=10000.0, read_bytes=0,
                       write_bytes=0, read_time=0.0, write_time=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "write rate degraded threshold", "25 bytes/sec")
        values.put_field(cifparser.ROOT_PATH, "write rate failed threshold", "75 bytes/sec")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskperformance import DiskPerformance
        check = DiskPerformance(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), FAILED)
