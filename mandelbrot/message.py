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

import json

class Message(object):
    """
    """
    def __init__(self, msgtype):
        self.msgtype = msgtype

    def __str__(self):
        return self.tojson()

    def __dump__(self):
        return {'messageType': self.msgtype}

class MandelbrotMessage(Message):
    """
    """
    def __init__(self, source, msgtype):
        Message.__init__(self, msgtype)
        self.source = source

    def __dump__(self):
        data = Message.__dump__(self)
        data['payload'] = {'source': self.source}
        return data

class StatusMessage(MandelbrotMessage):
    """
    """
    def __init__(self, source, health, summary, timestamp, detail=None):
        self.health = health
        self.summary = summary
        self.timestamp = timestamp
        self.detail = detail
        MandelbrotMessage.__init__(self, source, 'io.mandelbrot.message.StatusMessage')

    def __dump__(self):
        data = MandelbrotMessage.__dump__(self)
        status = data['payload']
        status.update({'health': self.health, 'summary': self.summary, 'timestamp': self.timestamp})
        if self.detail is not None:
            status['detail'] = self.detail
        return data

class MetricsMessage(MandelbrotMessage):
    """
    """
    def __init__(self, source, metrics, timestamp):
        self.metrics = metrics
        self.timestamp = timestamp
        MandelbrotMessage.__init__(self, source, 'io.mandelbrot.message.MetricsMessage')

    def tojson(self):
        msgdata = {'metrics': self.metrics, 'timestamp': self.timestamp}
        return self.message2json(msgdata)

class EventsMessage(MandelbrotMessage):
    """
    """
    def __init__(self, source, events, timestamp):
        self.events = events
        self.timestamp = timestamp
        MandelbrotMessage.__init__(self, objectid, 'io.mandelbrot.message.EventsMessage')

    def tojson(self):
        msgdata = {'events': self.events, 'timestamp': self.timestamp}
        return self.message2json(msgdata)

class SnapshotMessage(MandelbrotMessage):
    """
    """
    def __init__(self, source, snapshot, timestamp):
        self.snapshot = snapshot
        self.timestamp = timestamp
        MandelbrotMessage.__init__(self, source, 'io.mandelbrot.message.SnapshotMessage')

    def tojson(self):
        msgdata = {'snapshot': self.snapshot, 'timestamp': self.timestamp}
        return self.message2json(msgdata)
