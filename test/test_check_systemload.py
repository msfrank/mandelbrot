import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import HEALTHY, DEGRADED, FAILED

MockCPUtimes = collections.namedtuple('MockCPUTimes', [
    "user",  "system", "idle", "nice", "iowait", "irq", "softirq", "steal", "guest", "guest_nice" ])

class TestSystemLoad(unittest.TestCase):

    def test_execute_SystemLoad_check_healthy(self):
        "SystemLoad check should return healthy evaluation when not breaching threshold"
        with unittest.mock.patch('psutil.cpu_count') as cpu_count:
            cpu_count.return_value = 4
            with unittest.mock.patch('os.getloadavg') as getloadavg:
                getloadavg.return_value = [0.0, 0.0, 0.0]
                values = cifparser.ValueTree()
                ns = cifparser.Namespace(values)
                from mandelbrot.check.systemload import SystemLoad
                check = SystemLoad(ns)
                check.init()
                evaluation = check.execute()
                self.assertEqual(evaluation.get_health(), HEALTHY)

    def test_execute_SystemLoad_check_user_degraded(self):
        "SystemLoad check should return degraded evaluation when 1 minute average breaches degraded threshold"
        with unittest.mock.patch('psutil.cpu_count') as cpu_count:
            cpu_count.return_value = 4
            with unittest.mock.patch('os.getloadavg') as getloadavg:
                getloadavg.return_value = [1.5, 0.0, 0.0]
                values = cifparser.ValueTree()
                values.put_field(cifparser.ROOT_PATH, "1min degraded threshold", "1.0")
                values.put_field(cifparser.ROOT_PATH, "1min failed threshold", "2.0")
                ns = cifparser.Namespace(values)
                from mandelbrot.check.systemload import SystemLoad
                check = SystemLoad(ns)
                check.init()
                evaluation = check.execute()
                self.assertEqual(evaluation.get_health(), DEGRADED)

    def test_execute_SystemLoad_check_user_failed(self):
        "SystemLoad check should return failed evaluation when 1 minute average breaches failed threshold"
        with unittest.mock.patch('psutil.cpu_count') as cpu_count:
            cpu_count.return_value = 4
            with unittest.mock.patch('os.getloadavg') as getloadavg:
                getloadavg.return_value = [3.0, 0.0, 0.0]
                values = cifparser.ValueTree()
                values.put_field(cifparser.ROOT_PATH, "1min degraded threshold", "1.0")
                values.put_field(cifparser.ROOT_PATH, "1min failed threshold", "2.0")
                ns = cifparser.Namespace(values)
                from mandelbrot.check.systemload import SystemLoad
                check = SystemLoad(ns)
                check.init()
                evaluation = check.execute()
                self.assertEqual(evaluation.get_health(), FAILED)
