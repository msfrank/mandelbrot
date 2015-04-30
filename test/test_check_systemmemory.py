import bootstrap

import unittest
import unittest.mock
import cifparser
import collections

from mandelbrot.model.evaluation import HEALTHY, DEGRADED, FAILED

MockVMem = collections.namedtuple('MockVMem', ['total', 'available',
    'percent', 'used', 'free', 'active', 'inactive', 'buffers', 'cached',
    'wired', 'shared'])
MockSwap = collections.namedtuple('MockSwap', ['total', 'percent', 'used',
    'free', 'sin', 'sout'])

class TestSystemMemory(unittest.TestCase):

    @unittest.mock.patch('psutil.virtual_memory')
    @unittest.mock.patch('psutil.swap_memory')
    def test_execute_SystemMemory_check_healthy(self, swap_memory, virtual_memory):
        "SystemMemory check should return healthy evaluation when not breaching threshold"
        virtual_memory.return_value = MockVMem(total=100, available=100, percent=0.0,
            used=0, free=100, active=0, inactive=100, buffers=0, cached=0, wired=0, shared=0)
        swap_memory.return_value = MockSwap(total=100, percent=0.0, used=0, free=100, sin=0, sout=0)
        values = cifparser.ValueTree()
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemmemory import SystemMemory
        check = SystemMemory(ns)
        check.init()
        evaluation = check.execute()
        self.assertEqual(evaluation.get_health(), HEALTHY)

    @unittest.mock.patch('psutil.virtual_memory')
    @unittest.mock.patch('psutil.swap_memory')
    def test_execute_SystemMemory_check_memory_degraded(self, swap_memory, virtual_memory):
        "SystemMemory check should return degraded evaluation when memory breaches degraded threshold"
        virtual_memory.return_value = MockVMem(total=100, available=50, percent=50.0,
            used=50, free=50, active=50, inactive=0, buffers=0, cached=0, wired=0, shared=0)
        swap_memory.return_value = MockSwap(total=100, percent=0.0, used=0, free=100, sin=0, sout=0)
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "memory degraded threshold", "25 bytes")
        values.put_field(cifparser.ROOT_PATH, "memory failed threshold", "75 bytes")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemmemory import SystemMemory
        check = SystemMemory(ns)
        check.init()
        evaluation = check.execute()
        self.assertEqual(evaluation.get_health(), DEGRADED)

    @unittest.mock.patch('psutil.virtual_memory')
    @unittest.mock.patch('psutil.swap_memory')
    def test_execute_SystemMemory_check_memory_failed(self, swap_memory, virtual_memory):
        "SystemMemory check should return failed evaluation when memory breaches failed threshold"
        virtual_memory.return_value = MockVMem(total=100, available=10, percent=90.0,
            used=90, free=10, active=90, inactive=0, buffers=0, cached=0, wired=0, shared=0)
        swap_memory.return_value = MockSwap(total=100, percent=0.0, used=0, free=100, sin=0, sout=0)
        values = cifparser.ValueTree()
        values.put_field(cifparser.ROOT_PATH, "memory degraded threshold", "25 bytes")
        values.put_field(cifparser.ROOT_PATH, "memory failed threshold", "75 bytes")
        ns = cifparser.Namespace(values)
        from mandelbrot.check.systemmemory import SystemMemory
        check = SystemMemory(ns)
        check.init()
        evaluation = check.execute()
        self.assertEqual(evaluation.get_health(), FAILED)
