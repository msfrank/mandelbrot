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

from zope.interface import Interface, implements
from mandelbrot.mbobject import MBObject

class IProbe(Interface):

    def configure(self, section):
        ""

    def set_id(self, objectid):
        ""

    def get_id(self):
        ""

    def get_type(self):
        ""

    def get_metadata(self):
        ""

    def make_policy(self, parent):
        ""

    def probe(self):
        ""

class Probe(MBObject):
    implements(IProbe)

    def __init__(self):
        MBObject.__init__(self)
        self._objectid = None
        self._objecttype = None
        self._policy = None
        self.name = None
        self.description = None
        self.tags = None
        self.joining_timeout = None
        self.probe_timeout = None
        self.alert_timeout = None
        self.leaving_timeout = None
        self.flap_window = None
        self.flap_deviations = None
        self.notifications = None
        self.notification_policy = None

    def configure(self, section):
        # metadata parameters
        self.name = section.get_str('display name')
        self.description = section.get_str('description')
        self.tags = section.get_list('tags')
        # policy parameters
        self.joining_timeout = section.get_timedelta("joining timeout")
        self.probe_timeout = section.get_timedelta("probe timeout")
        self.alert_timeout = section.get_timedelta("alert timeout")
        self.leaving_timeout = section.get_timedelta("leaving timeout")
        self.notifications = section.get_list("notifications")
        self.merge_notifications = section.get_list("merge notifications")

    def set_id(self, objectid):
        if self._objectid is not None:
            raise AttributeError("id is already set")
        self._objectid = objectid

    def get_id(self):
        return self._objectid

    id = property(get_id, set_id)

    def get_type(self):
        return self._objecttype

    @property
    def type(self):
        return self.get_type()

    def get_metadata(self):
        metadata = {}
        if self.name is not None:
            metadata['prettyName'] = self.name
        if self.name is not None:
            metadata['description'] = self.description
        return metadata

    @property
    def metadata(self):
        return self.get_metadata()

    def make_policy(self, defaults):
        policy = {}
        if self.joining_timeout is not None:
            policy['joiningTimeout'] = self.joining_timeout
        else:
            policy['joiningTimeout'] = defaults.joining_timeout
        if self.probe_timeout is not None:
            policy['probeTimeout'] = self.probe_timeout
        else:
            policy['probeTimeout'] = defaults.probe_timeout
        if self.alert_timeout is not None:
            policy['alertTimeout'] = self.alert_timeout
        else:
            policy['alertTimeout'] = defaults.alert_timeout
        if self.leaving_timeout is not None:
            policy['leavingTimeout'] = self.leaving_timeout
        else:
            policy['leavingTimeout'] = defaults.leaving_timeout
        if self.notifications is not None:
            policy['notifications'] = set(self.notifications)
        elif defaults.notifications is not None:
            policy['notifications'] = set(defaults.notifications)
        if 'notifications' in policy and self.merge_notifications is not None:
            policy['notifications'] |= set(self.merge_notifications)
        return policy

    def probe(self):
        raise NotImplementedError()

class ScalarProbe(Probe):
    """
    """
    def configure(self, section):
        # policy parameters
        self.flap_window = section.get_timedelta("flap window", 0)
        self.flap_deviations = section.get_int("flap deviations", 0)

    def make_policy(self, defaults):
        policy = Probe.make_policy(self, defaults)
        behavior = dict()
        if self.flap_window is not None:
            behavior['flapWindow'] = self.flap_window
        else:
            behavior['flapWindow'] = defaults.scalar_flap_window
        if self.flap_deviations is not None:
            behavior['flapDeviations'] = self.flap_deviations
        else:
            behavior['flapDeviations'] = defaults.scalar_flap_deviations
        policy['behavior'] = { 'behaviorType': 'scalar', 'behaviorPolicy': behavior }
        return policy

class AggregateProbe(Probe):
    """
    """
    def configure(self, section):
        # policy parameters
        self.flap_window = section.get_timedelta("flap window", 0)
        self.flap_deviations = section.get_int("flap deviations", 0)

    def make_policy(self, defaults):
        policy = Probe.make_policy(self, defaults)
        behavior = dict()
        if self.flap_window is not None:
            behavior['flapWindow'] = self.flap_window
        else:
            behavior['flapWindow'] = defaults.aggregate_flap_window
        if self.flap_deviations is not None:
            behavior['flapDeviations'] = self.flap_deviations
        else:
            behavior['flapDeviations'] = defaults.aggregate_flap_deviations
        policy['behavior'] = { 'behaviorType': 'aggregate', 'behaviorPolicy': behavior }
        return policy


