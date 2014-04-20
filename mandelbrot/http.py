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
from zope.interface import implements
from twisted.web.client import Agent, ProxyAgent, HTTPConnectionPool, readBody
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.http')

def as_json(data):
    """
    """
    class JsonProducer(object):
        implements(IBodyProducer)
        def __init__(self, body):
            self.entity = json.dumps(body)
            self.length = len(self.entity)
        def startProducing(self, consumer):
            consumer.write(self.entity)
            return succeed(None)
        def pauseProducing(self):
            pass
        def stopProducing(self):
            pass
    return JsonProducer(data)

def from_json(data, proto=None):
    """
    """
    data = json.loads(data)
    if proto is None:
        return data
    if not hasattr(proto, '__load__'):
        raise AttributeError("proto %s has no __load__ attribute" % proto.__name__)
    return proto.__load__(data)

class Http(object):
    """
    """
    def __init__(self):
        from twisted.internet import reactor
        self.pool = HTTPConnectionPool(reactor)
        logger.debug("created HTTP connection pool")

    def agent(self, bind=None, timeout=None):
        from twisted.internet import reactor
        return Agent(reactor, pool=self.pool, bindAddress=bind, connectTimeout=timeout)

    def proxy(self, endpoint):
        from twisted.internet import reactor
        return ProxyAgent(endpoint, reactor, self.pool)

    def read_body(self, response):
        return readBody(response)

http = Http()
