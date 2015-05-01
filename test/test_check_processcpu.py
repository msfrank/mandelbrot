import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import *

class TestProcessCPU(unittest.TestCase):

    @unittest.mock.patch('time.time')
    def test_execute_ProcessCPU_check_healthy(self, time):
        "ProcessCPU check should return healthy evaluation when not breaching threshold"
        time.side_effect = [0.0, 100.0]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "process matches name", "foo")
        values.put_field(cifparser.ROOT_PATH, "extended summary", "true")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.processcpu import ProcessCPU
        check = ProcessCPU(ns)
        with unittest.mock.patch.object(check, 'get_process') as get_process:
            process = unittest.mock.Mock()
            process.pid = 42
            process.create_time = unittest.mock.Mock(return_value=0.0)
            process.cpu_times = unittest.mock.Mock(side_effect=[
                (0.0, 0.0),
                (0.0, 0.0),
            ])
            get_process.return_value = process
            evaluation = Evaluation()
            context = check.init()
            check.execute(evaluation, context)
            print(evaluation)
            self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('time.time')
    def test_execute_ProcessCPU_check_user_degraded(self, time):
        "ProcessCPU check should return degraded evaluation when user % breaches degraded threshold"
        time.side_effect = [0.0, 100.0]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "process matches name", "foo")
        values.put_field(cifparser.ROOT_PATH, "extended summary", "true")
        values.put_field(cifparser.ROOT_PATH, "user degraded threshold", "25%")
        values.put_field(cifparser.ROOT_PATH, "user failed threshold", "75%")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.processcpu import ProcessCPU
        check = ProcessCPU(ns)
        with unittest.mock.patch.object(check, 'get_process') as get_process:
            process = unittest.mock.Mock()
            process.pid = 42
            process.create_time = unittest.mock.Mock(return_value=0.0)
            process.cpu_times = unittest.mock.Mock(side_effect=[
                (0.0, 0.0),
                (50.0, 0.0),
            ])
            get_process.return_value = process
            evaluation = Evaluation()
            context = check.init()
            check.execute(evaluation, context)
            print(evaluation)
            self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('time.time')
    def test_execute_ProcessCPU_check_user_failed(self, time):
        "ProcessCPU check should return failed evaluation when user % breaches failed threshold"
        time.side_effect = [0.0, 100.0]
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "process matches name", "foo")
        values.put_field(cifparser.ROOT_PATH, "extended summary", "true")
        values.put_field(cifparser.ROOT_PATH, "user degraded threshold", "25%")
        values.put_field(cifparser.ROOT_PATH, "user failed threshold", "75%")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.processcpu import ProcessCPU
        check = ProcessCPU(ns)
        with unittest.mock.patch.object(check, 'get_process') as get_process:
            process = unittest.mock.Mock()
            process.pid = 42
            process.create_time = unittest.mock.Mock(return_value=0.0)
            process.cpu_times = unittest.mock.Mock(side_effect=[
                (0.0, 0.0),
                (100.0, 0.0),
            ])
            get_process.return_value = process
            evaluation = Evaluation()
            context = check.init()
            check.execute(evaluation, context)
            print(evaluation)
            self.assertEqual(evaluation.get_health(), FAILED)
