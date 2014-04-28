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

from urlparse import urlparse

class ProbeRef(object):
    """
    """
    def __init__(self, scheme, location, segments):
        self._scheme = scheme
        self._location = location
        self._segments = tuple(segments)

    def __str__(self):
        return self.uri + self.path

    @property
    def uri(self):
        if self._scheme is None or self._location is None:
            return ''
        return self._scheme + ":" + self._location

    @property
    def scheme(self):
        return self._scheme

    @property
    def location(self):
        return self._location

    @property
    def segments(self):
        return self._segments

    @property
    def path(self):
        return "/" + '/'.join(self._segments)

    def is_local(self):
        if self._uri is None:
            return True
        return False

def parse_proberef(string):
    string = string.strip()
    # special case 1: 
    if string == '/':
        return ProbeRef(None, None, [])
    segments = string.split('/')
    # special case 2: 
    if len(segments) == 1:
        return ProbeRef(None, None, segments)
    # handle absolute path, with or without uri
    if segments[0] == '':
        uri = None
    else:
        uri = segments[0]
    # verify there is a scheme and location part
    scheme,sep,location = uri.partition(':')
    if scheme,sep,location == (uri,'',''):
        raise Exception("invalid proberef %s: uri part is malformed" % string)
    # parse each segment in path
    path = list()
    for segment in segments[1:]:
        segment = segment.strip()
        if segment == '':
            raise Exception("invalid proberef %s: empty path segment is not allowed" % string)
        path.append(segment)
    return ProbeRef(scheme, location, path)
