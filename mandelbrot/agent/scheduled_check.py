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

import logging

log = logging.getLogger("mandelbrot.agent.scheduled_check")

import mandelbrot.check
import mandelbrot.registry

class ScheduledCheck(object):
    """
    """
    def __init__(self, check_id, check, delay, offset, jitter):
        """
        :param check_id:
        :type check_id: str
        :param check:
        :type check: mandelbrot.checks.Check
        :param delay:
        :type delay: float
        :param offset:
        :type offset: float
        :param jitter:
        :type jitter: float
        """
        self.check_id = check_id
        self.check = check
        self.delay = delay
        self.offset = offset
        self.jitter = jitter

def make_scheduled_check(instance_check, registry):
    """

    :param instance_check:
    :type instance_check: mandelbrot.instance.InstanceCheck
    :param registry:
    :type registry: mandelbrot.registry.Registry
    :rtype: ScheduledCheck
    """
    factory_name, _, requirement = instance_check.check_type.partition(':')
    if requirement == '':
        requirement = mandelbrot.registry.require_mandelbrot
    check_factory = registry.lookup_factory(mandelbrot.check.entry_point_type,
        factory_name, mandelbrot.check.Check, requirement)
    check = check_factory(instance_check.check_params)
    log.debug("instantiating check %s with requirement '%s'",
        instance_check.check_id, instance_check.check_type)
    scheduled_check = ScheduledCheck(instance_check.check_id, check,
        instance_check.delay, instance_check.offset, instance_check.jitter)
    return scheduled_check
