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
    def __init__(self, objectid, msgtype):
        self.objectid = objectid
        self.msgtype = msgtype

    VERSION = 1

    def __str__(self):
        return self.tojson()

    def message2json(self, msgdata):
        return json.dumps({
            'v': Message.VERSION,
            'objectId': self.objectid,
            'type': self.msgtype,
            'data': msgdata
            })

    def tojson(self):
        raise NotImplementedError()

class StatusMessage(Message):
    """
    """
    def __init__(self, objectid, state, summary, detail=None, timestamp=None):
        self.state = state
        self.summary = summary
        self.detail = detail
        self.timestamp = timestamp
        Message.__init__(self, objectid, 'io.mandelbrot.message.Status')

    def tojson(self):
        msgdata = {'state': self.state, 'summary': self.summary}
        if self.detail is not None:
            msgdata['detail'] = self.detail
        if self.timestamp is not None:
            msgdata['timestamp'] = self.timestamp
        return self.message2json(msgdata)

class MetricsMessage(Message):
    """
    """
    def __init__(self, objectid, metrics, timestamp=None):
        self.metrics = metrics
        self.timestamp = timestamp
        Message.__init__(self, objectid, 'io.mandelbrot.message.Metrics')

    def tojson(self):
        msgdata = {'metrics': self.metrics}
        if self.timestamp is not None:
            msgdata['timestamp'] = self.timestamp
        return self.message2json(msgdata)

class EventsMessage(Message):
    """
    """
    def __init__(self, objectid, events, timestamp=None):
        self.events = events
        self.timestamp = timestamp
        Message.__init__(self, objectid, 'io.mandelbrot.message.Events')

    def tojson(self):
        msgdata = {'events': self.events}
        if self.timestamp is not None:
            msgdata['timestamp'] = self.timestamp
        return self.message2json(msgdata)

class SnapshotMessage(Message):
    """
    """
    def __init__(self, objectid, snapshot, timestamp=None):
        self.snapshot = snapshot
        self.timestamp = timestamp
        Message.__init__(self, objectid, 'io.mandelbrot.message.Snapshot')

    def tojson(self):
        msgdata = {'snapshot': self.snapshot}
        if self.timestamp is not None:
            msgdata['timestamp'] = self.timestamp
        return self.message2json(msgdata)
