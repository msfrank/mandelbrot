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

import urlparse, pprint
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure
from twisted.web.http_headers import Headers
from mandelbrot.endpoints import *
from mandelbrot.message import ProbeMessage
from mandelbrot.http import http, as_json
from mandelbrot.loggers import getLogger
from mandelbrot import versionstring

logger = getLogger('mandelbrot.endpoints.http')

class HTTPEndpoint(Endpoint):
    """
    """
    def __init__(self):
        Endpoint.__init__(self)
        self._agent = None
        self.endpoint = None

    def configure(self, endpoint, section):
        self.endpoint = endpoint
        Endpoint.configure(self, endpoint, section)

    @property
    def agent(self):
        if self._agent is None:
            self._agent = http.agent()
        return self._agent

    @property
    def headers(self):
        return Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})

    def send(self, message):
        if not isinstance(message, ProbeMessage):
            raise TypeError("message must be a ProbeMessage")
        uri = str(message.source.uri)
        url = urlparse.urljoin(self.endpoint, 'objects/systems/' + uri + '/actions/submit')
        defer = self.agent.request('POST', url, self.headers, as_json(message))
        logger.debug("sending message to %s", url)
        def on_response(response):
            if response.code != 200:
                logger.debug("message was dropped by server: %i %s", response.code, response.phrase)
        def on_failure(failure):
            logger.debug("failed to send message: %s", failure.getErrorMessage())
        defer.addCallbacks(on_response, on_failure)

    def register(self, uri, registration):
        """
        """
        from twisted.internet import reactor
        result = Deferred()
        # callbacks
        def on_response(response):
            logger.debug("received response %s", response)
            if isinstance(response, Failure):
                result.errback(response)
            else:
                logger.debug("registration returned %i: %s", response.code, response.phrase)
                # registration accepted
                if response.code == 202:
                    result.callback(uri)
                # conflicts with existing system
                elif response.code == 409:
                    result.errback(ResourceConflict())
                # unknown error, fail fast and loud
                else:
                    def read_failure(body):
                        logger.debug("HTTP response entity was:\n----\n" + body + "\n----")
                        result.errback(EndpointError("registration encountered a fatal error"))
                    http.read_body(response).addCallback(read_failure)
        url = urlparse.urljoin(self.endpoint, 'objects/systems')
        logger.info("registering system %s", uri)
        logger.debug("POST %s", url)
        defer = self.agent.request('POST', url, self.headers, as_json({'uri': uri, 'registration': registration.__dump__()})) 
        defer.addBoth(on_response)
        return result

    def update(self, uri, registration):
        """
        """
        from twisted.internet import reactor
        result = Deferred()
        # callbacks
        def on_response(response):
            logger.debug("received response %s", response)
            if isinstance(response, Failure):
                result.errback(response)
            else:
                logger.debug("registration returned %i: %s", response.code, response.phrase)
                # registration accepted
                if response.code == 202:
                    result.callback(uri)
                # system doesn't exist
                elif response.code == 404:
                    result.errback(ResourceNotFound())
                # unknown error, fail fast and loud
                else:
                    def read_failure(body):
                        logger.debug("HTTP response entity was:\n----\n" + body + "\n----")
                        result.errback(EndpointError("registration encountered a fatal error"))
                    http.read_body(response).addCallback(read_failure)
        url = urlparse.urljoin(self.endpoint, 'objects/systems/' + uri)
        logger.info("updating system %s", uri)
        logger.debug("PUT %s", url)
        defer = self.agent.request('PUT', url, self.headers, as_json({'uri': uri, 'registration': registration.__dump__()})) 
        defer.addBoth(on_response)
        return result

    def unregister(self, uri):
        raise NotImplementedError()
