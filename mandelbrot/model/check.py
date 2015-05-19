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
import cifparser

from mandelbrot.model import StructuredMixin

class Check(StructuredMixin):
    """
    """
    def __init__(self):
        self.check_id = None
        self.behavior_type = None
        self.policy = {}
        self.properties = {}
        self.metadata = {}

    def get_check_id(self):
        return self.check_id

    def set_check_id(self, check_id):
        assert isinstance(check_id, cifparser.Path)
        self.check_id = check_id

    def get_behavior_type(self):
        return self.behavior_type

    def set_behavior_type(self, behavior_type):
        assert isinstance(behavior_type, str)
        self.behavior_type = behavior_type

    def get_join_timeout(self):
        return self.policy['joiningTimeout']

    def set_join_timeout(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['joiningTimeout'] = int(timeout / datetime.timedelta(milliseconds=1))

    def get_check_timeout(self):
        return self.policy['checkTimeout']

    def set_check_timeout(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['checkTimeout'] = int(timeout / datetime.timedelta(milliseconds=1))

    def get_alert_timeout(self):
        return self.policy['alertTimeout']

    def set_alert_timeout(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['alertTimeout'] = int(timeout / datetime.timedelta(milliseconds=1))

    def get_retirement_age(self):
        return self.policy['leavingTimeout']

    def set_retirement_age(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['leavingTimeout'] = int(timeout / datetime.timedelta(milliseconds=1))

    def get_property(self, property_name):
        return self.properties[property_name]

    def list_properties(self):
        return self.properties.items()

    def set_property(self, property_name, property_value):
        assert isinstance(property_name, str)
        assert isinstance(property_value, str)
        self.properties[property_name] = property_value

    def delete_property(self, property_name):
        del self.properties[property_name]

    def flush_properties(self):
        self.properties = {}

    def get_meta_value(self, meta_name):
        return self.metadata[meta_name]

    def list_metadata(self):
        return self.metadata.items()

    def set_meta_value(self, meta_name, meta_value):
        assert isinstance(meta_name, str)
        assert isinstance(meta_value, str)
        self.metadata[meta_name] = meta_value

    def delete_meta_value(self, meta_name):
        del self.metadata[meta_name]

    def flush_metadata(self):
        self.metadata = {}

    def destructure(self):
        structure = {}
        structure['checkType'] = self.behavior_type
        structure['policy'] =  self.policy
        structure['properties'] = self.properties
        structure['metadata'] = self.metadata
        return structure
