# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import pkg_resources
import logging

log = logging.getLogger("mandelbrot.registry")

from mandelbrot import versionstring
require_mandelbrot = 'mandelbrot == ' + versionstring()

class Registry(object):
    """
    """
    def __init__(self):
        self.env = pkg_resources.Environment([])
        plugins,errors = pkg_resources.working_set.find_plugins(self.env)
        for plugin in plugins:
            pkg_resources.working_set.add(plugin)
        for error in errors:
            log.info("failed to load distribution: %s", error)
        self.overrides = {}

    def override_factory(self, entry_point_type, factory_name, factory):
        """
        :param entry_point_type:
        :type entry_point_type: str
        :param factory_name:
        :type factory_name: str
        :param factory:
        :type factory: type
        """
        self.overrides[(entry_point_type,factory_name)] = factory

    def lookup_factory(self, entry_point_type, factory_name, factory_type, requirement=require_mandelbrot):
        """
        :param entry_point_type:
        :type entry_point_type: str
        :param factory_name:
        :type factory_name: str
        :param factory_type:
        :type factory_type: type
        :param requirement:
        :type requirement: str
        """
        log.debug("looking up '%s' of type %s with requirement %s", factory_name, 
            entry_point_type, requirement)
        # check factory overrides first
        if (entry_point_type,factory_name) in self.overrides:
            factory = self.overrides[(entry_point_type,factory_name)]
        # find the entrypoint matching the specified requirement
        else:
            requirement = pkg_resources.Requirement.parse(requirement)
            distribution = pkg_resources.working_set.find(requirement)
            factory = distribution.load_entry_point(entry_point_type, factory_name)
        log.debug("loaded factory %s.%s", factory.__module__, factory.__class__.__name__)
        # verify that the factory is the correct type
        if not issubclass(factory, factory_type):
            raise TypeError("{}.{} is not a subclass of {}".format(
                factory.__module__, factory.__class__.__name__, factory_type.__name__))
        return factory
