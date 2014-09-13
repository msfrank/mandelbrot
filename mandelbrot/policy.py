# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
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

class OverridePolicy(object):
    def __init__(self, joining_timeout=None, probe_timeout=None, alert_timeout=None, leaving_timeout=None, notifications=None):
        self.joining_timeout = joining_timeout
        self.probe_timeout = probe_timeout
        self.alert_timeout = alert_timeout
        self.leaving_timeout = leaving_timeout
        self.notifications = notifications

    def merge(self, override):
        joining_timeout = override.joining_timeout if override.joining_timeout is not None else self.joining_timeout
        probe_timeout = override.probe_timeout if override.probe_timeout is not None else self.probe_timeout
        alert_timeout = override.alert_timeout if override.alert_timeout is not None else self.alert_timeout
        leaving_timeout = override.leaving_timeout if override.leaving_timeout is not None else self.leaving_timeout
        if isinstance(override.notifications, frozenset):
            notifications = override.notifications
        if isinstance(override.notifications, set):
            notifications = self.notifications.union(override.notifications)
        else:
            notifications = self.notifications
        return OverridePolicy(joining_timeout=joining_timeout,
                              probe_timeout=probe_timeout,
                              alert_timeout=alert_timeout,
                              leaving_timeout=leaving_timeout,
                              notifications=notifications)

class Policy(object):
    def __init__(self, joining_timeout, probe_timeout, alert_timeout, leaving_timeout, notifications):
        if not isinstance(joining_timeout, datetime.timedelta):
            raise ValueError("joining_timeout must be a timedelta")
        if not isinstance(probe_timeout, datetime.timedelta):
            raise ValueError("probe_timeout must be a timedelta")
        if not isinstance(alert_timeout, datetime.timedelta):
            raise ValueError("alert_timeout must be a timedelta")
        if not isinstance(leaving_timeout, datetime.timedelta):
            raise ValueError("leaving_timeout must be a timedelta")
        self.joining_timeout = joining_timeout
        self.probe_timeout = probe_timeout
        self.alert_timeout = alert_timeout
        self.leaving_timeout = leaving_timeout
        self.notifications = notifications

    def parse(self, section):
        joining_timeout = section.get_timedelta("joining timeout", None)
        probe_timeout = section.get_timedelta("probe timeout", None)
        alert_timeout = section.get_timedelta("alert timeout", None)
        leaving_timeout = section.get_timedelta("leaving timeout", None)
        notifications = section.get_list("notifications", None)
        override = OverridePolicy(joining_timeout, probe_timeout, alert_timeout, leaving_timeout, notifications)
        return self.merge(override)

    def merge(self, override):
        joining_timeout = override.joining_timeout if override.joining_timeout is not None else self.joining_timeout
        probe_timeout = override.probe_timeout if override.probe_timeout is not None else self.probe_timeout
        alert_timeout = override.alert_timeout if override.alert_timeout is not None else self.alert_timeout
        leaving_timeout = override.leaving_timeout if override.leaving_timeout is not None else self.leaving_timeout
        if isinstance(override.notifications, frozenset):
            notifications = override.notifications
        if isinstance(override.notifications, set):
            notifications = self.notifications.union(override.notifications)
        else:
            notifications = self.notifications
        return Policy(joining_timeout=joining_timeout,
                      probe_timeout=probe_timeout,
                      alert_timeout=alert_timeout,
                      leaving_timeout=leaving_timeout,
                      notifications=notifications)

    def __dump__(self):
        spec = dict()
        spec['joiningTimeout'] = self.joining_timeout
        spec['probeTimeout'] = self.probe_timeout
        spec['alertTimeout'] = self.alert_timeout
        spec['leavingTimeout'] = self.leaving_timeout
        if self.notifications is not None:
            spec['notifications'] = self.notifications
        return spec
