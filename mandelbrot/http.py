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

import json, datetime, time, pprint
from zope.interface import implements
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.http')

class JSONDecoder(json.JSONDecoder):
    pass

class JSONEncoder(json.JSONEncoder):
    """
    Upgraded json encoder which can dump extra data types such as timedelta.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            seconds = time.mktime(o.utctimetuple())
            return long(seconds * 1000)
        if isinstance(o, datetime.timedelta):
            seconds = (float(o.microseconds) + (float(o.seconds) + float(o.days) * 24.0 * 3600.0) * 10**6) / 10**6
            return long(seconds * 1000)
        return json.JSONEncoder.default(self, o)

json_decoder = JSONDecoder()
json_encoder = JSONEncoder()

class JsonProducer(object):
    implements(IBodyProducer)
    def __init__(self, data):
        #logger.debug("entity:\n%s", pprint.pformat(data))
        self.entity = json_encoder.encode(data)
        self.length = len(self.entity)
    def startProducing(self, consumer):
        consumer.write(self.entity)
        return succeed(None)
    def pauseProducing(self):
        pass
    def stopProducing(self):
        pass

def as_json(data):
    """
    """
    if hasattr(data, '__dump__'):
        return JsonProducer(data.__dump__())
    return JsonProducer(data)

def from_json(data, proto=None):
    """
    """
    data = json_decoder.decode(data)
    if proto is None:
        return data
    if not hasattr(proto, '__load__'):
        raise AttributeError("proto %s has no __load__ attribute" % proto.__name__)
    return proto.__load__(data)

class Http(object):
    """
    """
    def __init__(self):
        self._pool = None

    @property
    def pool(self):
        return None
        from twisted.web.client import HTTPConnectionPool
        if self._pool is None:
            self._pool = HTTPConnectionPool(self.reactor)
        #return self._pool

    @property
    def reactor(self):
        from twisted.internet import reactor
        return reactor

    def agent(self, bind=None, timeout=None):
        from twisted.web.client import Agent
        return Agent(self.reactor, pool=self.pool, bindAddress=bind, connectTimeout=timeout)

    def proxy(self, endpoint):
        from twisted.web.client import ProxyAgent
        return ProxyAgent(endpoint, self.reactor, self.pool)

    def read_body(self, response):
        from twisted.web.client import readBody
        return readBody(response)

http = Http()
