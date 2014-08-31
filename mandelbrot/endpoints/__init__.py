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

from zope.interface import Interface, implements

class IEndpoint(Interface):

    def configure(self, endpoint, settings):
        ""

    def send(self, message):
        ""

    def register(self, uri, registration):
        ""

    def update(self, uri, registration):
        ""

    def unregister(self, uri):
        ""
 
class Endpoint(object):
    """
    """
    def configure(self, endpoint, settings):
        pass

class ResourceConflict(Exception):
    """
    """

class ResourceNotFound(Exception):
    """
    """

class EndpointError(Exception):
    """
    """
