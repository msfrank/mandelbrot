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

import datetime
import pprint
import logging
from cifparser import or_default

log = logging.getLogger("mandelbrot.agent.registration")

from mandelbrot.model.registration import Registration
from mandelbrot.model.check import Check

default_join_timeout = datetime.timedelta(minutes=5)
default_check_timeout = datetime.timedelta(minutes=1)
default_alert_timeout = datetime.timedelta(minutes=2)
default_retirement_age = datetime.timedelta(days=1)
default_retention_period = datetime.timedelta(days=30)

def make_registration(agent_id, metadata, scheduled_checks):
    """
    :param agent_id:
    :type agent_id: cifparser.Path
    :param metadata:
    :type metadata: list[(str,str)]
    :param scheduled_checks:
    :type scheduled_checks: list[ScheduledCheck]
    :param defaults:
    """
    registration = Registration()
    registration.set_agent_type("mandelbrot")

    # set agent id
    registration.set_agent_id(agent_id)

    # set policy
    registration.set_retention_period(default_retention_period)

    # set metadata
    for meta_name,meta_value in metadata:
        registration.set_meta_value(meta_name, meta_value)

    # note that scheduled_checks is ordered by check_id
    for scheduled_check in scheduled_checks:
        check_id = scheduled_check.check_id
        check = Check()
        check.set_check_id(check_id)
        # check must implement get_behavior_type()
        check.set_behavior_type(scheduled_check.check.get_behavior_type())
        # if policy parameters aren't specified, use agent or application default
        join_timeout = or_default(default_join_timeout, scheduled_check.check.get_join_timeout)
        check.set_join_timeout(join_timeout)
        alert_timeout = or_default(default_alert_timeout, scheduled_check.check.get_alert_timeout)
        check.set_alert_timeout(alert_timeout)
        check_timeout = or_default(default_check_timeout, scheduled_check.check.get_check_timeout)
        check.set_check_timeout(check_timeout)
        retirement_age = or_default(default_retirement_age, scheduled_check.check.get_retirement_age)
        check.set_retirement_age(retirement_age)
        registration.set_check(check_id, check)

    s = pprint.pformat(registration.destructure(), indent=4, width=120, compact=False)
    log.debug("registration for %s:\n%s", agent_id, s)

    return registration
