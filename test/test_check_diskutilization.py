import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import *

MockDiskUsage = collections.namedtuple('MockDiskUsage', ['total', 'used', 'free', 'percent'])

class TestDiskUtilization(unittest.TestCase):

    @unittest.mock.patch('psutil.disk_usage')
    def test_execute_DiskUtilization_check_healthy(self, disk_usage):
        "DiskUtilization check should return healthy evaluation when not breaching threshold"
        disk_usage.return_value = MockDiskUsage(total=100, percent=0.0, used=0, free=100)
        values = cifparser.ValueTree()
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskutilization import DiskUtilization
        check = DiskUtilization(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.disk_usage')
    def test_execute_DiskUtilization_check_memory_degraded(self, disk_usage):
        "DiskUtilization check should return degraded evaluation when disk breaches degraded threshold"
        disk_usage.return_value = MockDiskUsage(total=100, percent=50.0, used=50, free=50)
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "disk degraded threshold", "25 bytes")
        values.put_field(cifparser.ROOT_PATH, "disk failed threshold", "75 bytes")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskutilization import DiskUtilization
        check = DiskUtilization(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.disk_usage')
    def test_execute_DiskUtilization_check_memory_failed(self, disk_usage):
        "DiskUtilization check should return failed evaluation when disk breaches failed threshold"
        disk_usage.return_value = MockDiskUsage(total=100, percent=100.0, used=100, free=0)
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "disk degraded threshold", "25 bytes")
        values.put_field(cifparser.ROOT_PATH, "disk failed threshold", "75 bytes")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.diskutilization import DiskUtilization
        check = DiskUtilization(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), FAILED)
