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

from mandelbrot.model import StructuredMixin, add_constructor, construct
from mandelbrot.model.timestamp import Timestamp

class Notification(StructuredMixin):
    """
    """
    def __init__(self):
        self.check_ref = None
        self.timestamp = None
        self.kind = None
        self.description = None
        self.correlation = None

    def get_check_ref(self):
        return self.check_ref

    def set_check_ref(self, check_ref):
        assert isinstance(check_ref, str)
        self.check_ref = check_ref

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        assert isinstance(timestamp, Timestamp)
        self.timestamp = timestamp

    def get_kind(self):
        return self.kind

    def set_kind(self, kind):
        assert isinstance(kind, str)
        self.kind = kind

    def get_description(self):
        return self.description

    def set_description(self, description):
        assert isinstance(description, str)
        self.description = description

    def get_correlation(self):
        return self.correlation

    def set_correlation(self, correlation):
        assert isinstance(correlation, str)
        self.correlation = correlation

    def destructure(self):
        structure = {}
        structure['checkRef'] = self.check_ref
        structure['timestamp'] = self.timestamp.destructure()
        structure['kind'] = self.kind
        structure['description'] = self.description
        if self.correlation:
            structure['correlation'] = self.correlation
        return structure

def _construct_notification(structure):
    notification = Notification()
    notification.set_check_ref(structure['checkRef'])
    timestamp = construct(Timestamp, structure['timestamp'])
    notification.set_timestamp(timestamp)
    notification.set_kind(structure['kind'])
    notification.set_description(structure['description'])
    if 'correlation' in structure:
        notification.set_correlation(structure['correlation'])
    return notification

add_constructor(Notification, _construct_notification)
