import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import *

class TestSystemLoad(unittest.TestCase):

    @unittest.mock.patch('psutil.cpu_count')
    @unittest.mock.patch('os.getloadavg')
    def test_execute_SystemLoad_check_healthy(self, getloadavg, cpu_count):
        "SystemLoad check should return healthy evaluation when not breaching threshold"
        cpu_count.return_value = 4
        getloadavg.return_value = [0.0, 0.0, 0.0]
        values = cifparser.ValueTree()
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemload import SystemLoad
        check = SystemLoad(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.cpu_count')
    @unittest.mock.patch('os.getloadavg')
    def test_execute_SystemLoad_check_user_degraded(self, getloadavg, cpu_count):
        "SystemLoad check should return degraded evaluation when 1 minute average breaches degraded threshold"
        cpu_count.return_value = 4
        getloadavg.return_value = [1.5, 0.0, 0.0]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "1min degraded threshold", "1.0")
        values.put_field(cifparser.ROOT_PATH, "1min failed threshold", "2.0")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemload import SystemLoad
        check = SystemLoad(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.cpu_count')
    @unittest.mock.patch('os.getloadavg')
    def test_execute_SystemLoad_check_user_failed(self, getloadavg, cpu_count):
        "SystemLoad check should return failed evaluation when 1 minute average breaches failed threshold"
        cpu_count.return_value = 4
        getloadavg.return_value = [3.0, 0.0, 0.0]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "1min degraded threshold", "1.0")
        values.put_field(cifparser.ROOT_PATH, "1min failed threshold", "2.0")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemload import SystemLoad
        check = SystemLoad(ns)
        evaluation = Evaluation()
        context = check.init()
        check.execute(evaluation, context)
        self.assertEqual(evaluation.get_health(), FAILED)
