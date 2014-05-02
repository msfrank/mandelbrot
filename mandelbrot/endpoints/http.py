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

import urlparse
from twisted.web.http_headers import Headers
from mandelbrot.endpoints import Endpoint
from mandelbrot.message import Message, MandelbrotMessage
from mandelbrot.http import http, as_json
from mandelbrot.loggers import getLogger
from mandelbrot import versionstring

logger = getLogger('mandelbrot.endpoints.http')

class HTTPEndpoint(Endpoint):
    """
    """
    def __init__(self):
        Endpoint.__init__(self)
        self.agent = None

    def configure(self, section):
        self.endpoint = section.get_str("endpoint url")
        Endpoint.configure(self, section)

    def send(self, message):
        if self.agent is None:
            self.agent = http.agent()
        if isinstance(message, MandelbrotMessage):
            uri = message.source.split('/')[0]
            url = urlparse.urljoin(self.endpoint, 'objects/systems/' + uri + '/actions/submit')
            headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
            defer = self.agent.request('POST', url, headers, as_json(message))
            logger.debug("sending message to %s", url)
            defer.addErrback(self.onfailure)

    def onfailure(self, failure):
        logger.debug("failed to send message: %s", failure.getErrorMessage())
