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

import pprint
from twisted.internet.defer import succeed
from mandelbrot.endpoints import Endpoint
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.endpoints.dummy')

class DummyEndpoint(Endpoint):
    """
    """
    def configure(self, endpoint, settings):
        pass

    def send(self, message):
        logger.debug("received message: %s", message)

    def register(self, uri, registration):
        logger.debug("registering uri %s using registration:\n%s", uri, registration)
        return succeed(uri)

    def update(self, uri, registration):
        logger.debug("updating uri %s using registration:\n%s", uri, registration)
        return succeed(uri)

    def unregister(self, uri):
        logger.debug("unregistering uri %s", uri)
        return succeed(uri)
 
