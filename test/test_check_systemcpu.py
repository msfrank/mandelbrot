import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import *

MockCPUtimes = collections.namedtuple('MockCPUTimes', [
    "user",  "system", "idle", "nice", "iowait", "irq", "softirq", "steal", "guest", "guest_nice" ])

class TestSystemCPU(unittest.TestCase):

    @unittest.mock.patch('psutil.cpu_times')
    @unittest.mock.patch('time.time')
    def test_execute_SystemCPU_check_healthy(self, time, cpu_times):
        "SystemCPU check should return healthy evaluation when not breaching threshold"
        time.side_effect = [0.0, 100.0]
        cpu_times.side_effect = [
            MockCPUtimes(user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0,
                irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0),
            MockCPUtimes(user=0.0, system=0.0, idle=100.0, nice=0.0, iowait=0.0,
                irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "extended summary", "true")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemcpu import SystemCPU
        check = SystemCPU(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.cpu_times')
    @unittest.mock.patch('time.time')
    def test_execute_SystemCPU_check_user_degraded(self, time, cpu_times):
        "SystemCPU check should return degraded evaluation when user % breaches degraded threshold"
        time.side_effect = [0.0, 100.0]
        cpu_times.side_effect = [
            MockCPUtimes(user=0.0, system=0.0, idle=50.0, nice=0.0, iowait=0.0,
                irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0),
            MockCPUtimes(user=50.0, system=0.0, idle=50.0, nice=0.0, iowait=0.0,
                irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "extended summary", "true")
        values.put_field(cifparser.ROOT_PATH, "user degraded threshold", "25%")
        values.put_field(cifparser.ROOT_PATH, "user failed threshold", "75%")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemcpu import SystemCPU
        check = SystemCPU(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.cpu_times')
    @unittest.mock.patch('time.time')
    def test_execute_SystemCPU_check_user_failed(self, time, cpu_times):
        "SystemCPU check should return failed evaluation when user % breaches failed threshold"
        time.side_effect = [0.0, 100.0]
        cpu_times.side_effect = [
            MockCPUtimes(user=0.0, system=0.0, idle=0.0,nice=0.0, iowait=0.0,
                irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0),
            MockCPUtimes(user=100.0, system=0.0, idle=0.0,nice=0.0, iowait=0.0,
                irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0),
            ]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "extended summary", "true")
        values.put_field(cifparser.ROOT_PATH, "user degraded threshold", "25%")
        values.put_field(cifparser.ROOT_PATH, "user failed threshold", "75%")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemcpu import SystemCPU
        check = SystemCPU(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        print(evaluation)
        self.assertEqual(evaluation.get_health(), FAILED)
