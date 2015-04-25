import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import HEALTHY, DEGRADED, FAILED

MockCPUtimes = collections.namedtuple('MockCPUTimes', [
    "user",  "system", "idle", "nice", "iowait", "irq", "softirq", "steal", "guest", "guest_nice" ])

class TestSystemCPU(unittest.TestCase):

    def test_execute_SystemCPU_check_healthy(self):
        "SystemCPU check should return healthy evaluation when not breaching threshold"
        mockcputimes = MockCPUtimes(user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0,
            irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0)
        with unittest.mock.patch('psutil.cpu_times_percent') as cpu_times_percent:
            cpu_times_percent.return_value = mockcputimes
            values = cifparser.ValueTree()
            ns = cifparser.Namespace(values)
            from mandelbrot.check.systemcpu import SystemCPU
            check = SystemCPU(ns)
            check.init()
            evaluation = check.execute()
            self.assertEqual(evaluation.get_health(), HEALTHY)

    def test_execute_SystemCPU_check_user_degraded(self):
        "SystemCPU check should return degraded evaluation when user % breaches degraded threshold"
        mockcputimes = MockCPUtimes(user=50.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0,
            irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0)
        with unittest.mock.patch('psutil.cpu_times_percent') as cpu_times_percent:
            cpu_times_percent.return_value = mockcputimes
            values = cifparser.ValueTree()
            values.put_field(cifparser.ROOT_PATH, "user degraded threshold", "25%")
            values.put_field(cifparser.ROOT_PATH, "user failed threshold", "75%")
            ns = cifparser.Namespace(values)
            from mandelbrot.check.systemcpu import SystemCPU
            check = SystemCPU(ns)
            check.init()
            evaluation = check.execute()
            self.assertEqual(evaluation.get_health(), DEGRADED)

    def test_execute_SystemCPU_check_user_failed(self):
        "SystemCPU check should return failed evaluation when user % breaches failed threshold"
        mockcputimes = MockCPUtimes(user=100.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0,
            irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0)
        with unittest.mock.patch('psutil.cpu_times_percent') as cpu_times_percent:
            cpu_times_percent.return_value = mockcputimes
            values = cifparser.ValueTree()
            values.put_field(cifparser.ROOT_PATH, "user degraded threshold", "25%")
            values.put_field(cifparser.ROOT_PATH, "user failed threshold", "75%")
            ns = cifparser.Namespace(values)
            from mandelbrot.check.systemcpu import SystemCPU
            check = SystemCPU(ns)
            check.init()
            evaluation = check.execute()
            self.assertEqual(evaluation.get_health(), FAILED)
