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
from mandelbrot.mbobject import MBObject

class ISystem(Interface):

    def configure(self, systemtype, settings, metadata, policy):
        ""

    def get_uri(self):
        ""

    def get_type(self):
        ""

    def get_metadata(self):
        ""

    def get_policy(self):
        ""

    def get_probe(self, name):
        ""

    def set_probe(self, name, probe):
        ""

    def iter_probes(self):
        ""

    def describe(self):
        ""

class System(object):
    """
    """
    def __init__(self):
        self._uri = None
        self._systemtype = None
        self._metadata = None
        self._policy = None
        self._probes = dict()

    def configure(self, uri, systemtype, metadata, policy):
        self._uri = uri
        self._systemtype = systemtype
        self._metadata = metadata
        self._policy = policy

    def get_uri(self):
        return self._uri

    def get_type(self):
        return self._systemtype

    def get_metadata(self):
        return self._metadata

    def get_policy(self):
        return self._policy

    def get_probe(self, name):
        return self._probes[name]

    def set_probe(self, name, probe):
        self._probes[name] = probe

    def iter_probes(self):
        return self._probes.iteritems()
