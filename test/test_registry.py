import bootstrap

import unittest

from mandelbrot.registry import Registry
from mandelbrot.check import Check, entry_point_type
from mandelbrot.check.dummy import AlwaysHealthy
from mandelbrot import versionstring

class TestRegistry(unittest.TestCase):

    def test_lookup_check(self):
        "A Registry should lookup a check"
        registry = Registry()
        factory = registry.lookup_factory(entry_point_type, 'AlwaysHealthy', Check)
        self.assertIs(factory, AlwaysHealthy)

    def test_lookup_check_with_requirement(self):
        "A Registry should lookup a check with a specified requirement"
        registry = Registry()
        factory = registry.lookup_factory(entry_point_type,
            'AlwaysHealthy', Check, "mandelbrot == " + versionstring())
        self.assertIs(factory, AlwaysHealthy)

    def test_lookup_check_fails_when_check_type_not_exists(self):
        "A Registry should raise Exception when lookup check type doesn't exist"
        registry = Registry()
        self.assertRaises(Exception, registry.lookup_factory,
            entry_point_type, 'NotExists', Check)

    def test_lookup_check_fails_when_requirement_not_satisfied(self):
        "A Registry should raise Exception when lookup requirement is not satisfied"
        registry = Registry()
        self.assertRaises(Exception, registry.lookup_factory,
            entry_point_type, 'AlwaysHealthy', Check, "mandelbrot > " + versionstring())
