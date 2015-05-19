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

from mandelbrot.model import StructuredMixin, add_constructor, construct
from mandelbrot.model.notification import Notification
from mandelbrot.model.timestamp import Timestamp

class CheckNotifications(StructuredMixin):
    """
    """
    def __init__(self):
        self.timestamp = None
        self.notifications = []

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        assert isinstance(timestamp, Timestamp)
        self.timestamp = timestamp

    def append_notification(self, notification):
        assert isinstance(notification, Notification)
        return self.notifications.append(notification)

    def list_notifications(self):
        return self.notifications

    def destructure(self):
        structure = {}
        structure['timestamp'] = self.timestamp.destructure()
        structure['notifications'] = [n.destructure() for n in self.notifications]
        return structure

class CheckNotificationsPage(StructuredMixin):
    """
    """
    def __init__(self):
        self.check_notifications = []
        self.last = None
        self.exhausted = None

    def append_check_notifications(self, check_notifications):
        assert isinstance(check_notifications, CheckNotifications)
        return self.check_notifications.append(check_notifications)

    def list_check_notifications(self):
        return self.check_notifications

    def get_last(self):
        return self.last

    def set_last(self, last):
        assert isinstance(last, str)
        self.last = last

    def get_exhausted(self):
        return self.exhausted

    def set_exhausted(self, exhausted):
        assert isinstance(exhausted, bool)
        self.exhausted = exhausted

    def destructure(self):
        structure = {}
        return structure

def _construct_check_notifications(structure):
    check_notifications = CheckNotifications()
    timestamp = construct(Timestamp, structure['timestamp'])
    check_notifications.set_timestamp(timestamp)
    for value in structure['notifications']:
        notification = construct(Notification, value)
        check_notifications.append_notification(notification)
    return check_notifications

add_constructor(CheckNotifications, _construct_check_notifications)

def _construct_check_notifications_page(structure):
    page = CheckNotificationsPage()
    for value in structure['history']:
        check_notifications = construct(CheckNotifications, value)
        page.append_check_notifications(check_notifications)
    if 'last' in structure:
        page.set_last(structure['last'])
    if 'exhausted' in structure:
        page.set_exhausted(structure['exhausted'])
    return page

add_constructor(CheckNotificationsPage, _construct_check_notifications_page)
