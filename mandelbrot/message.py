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

import json, pprint
from mandelbrot.ref import ProbeRef

class Message(object):
    """
    """
    def __init__(self, msgtype):
        self.msgtype = msgtype

    def __str__(self):
        return pprint.pformat(self.__dump__())

    def __dump__(self):
        return {'messageType': self.msgtype}

class ProbeMessage(Message):
    """
    """
    def __init__(self, source, msgtype):
        Message.__init__(self, msgtype)
        if not isinstance(source, ProbeRef):
            raise TypeError("source must be a ProbeRef")
        self.source = source

    def __dump__(self):
        data = Message.__dump__(self)
        data['payload'] = {'source': str(self.source)}
        return data

class StatusMessage(ProbeMessage):
    """
    """
    def __init__(self, source, health, summary, timestamp):
        ProbeMessage.__init__(self, source, 'io.mandelbrot.message.StatusMessage')
        self.health = health
        self.summary = summary
        self.timestamp = timestamp

    def __dump__(self):
        data = ProbeMessage.__dump__(self)
        status = data['payload']
        status.update({'health': self.health, 'summary': self.summary, 'timestamp': self.timestamp})
        return data

class MetricsMessage(ProbeMessage):
    """
    """
    def __init__(self, source, metrics, timestamp):
        self.metrics = metrics
        self.timestamp = timestamp
        ProbeMessage.__init__(self, source, 'io.mandelbrot.message.MetricsMessage')

    def __dump__(self):
        data = ProbeMessage.__dump__(self)
        status = data['payload']
        status.update({'metrics': self.metrics, 'timestamp': self.timestamp})
        return data
