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

class SystemURI(object):
    """
    """
    def __init__(self, scheme, location):
        self._scheme = scheme
        self._location = location

    def __str__(self):
        return self._scheme + ":" + self._location

    @property
    def scheme(self):
        return self._scheme

    @property
    def location(self):
        return self._location

def parse_systemuri(string):
    """
    """
    string = string.strip()
    # verify there are no slashes in the uri
    if len(string.split('/')) != 1:
        raise Exception("invalid uri %s: forward slashes are not allowed in uri" % string)
    # verify there is a scheme and location part
    scheme,sep,location = string.partition(':')
    if (scheme,sep,location) == (string,'',''):
        raise Exception("invalid uri %s: scheme is missing" % string)
    return SystemURI(scheme, location)

class ProbeRef(object):
    """
    """
    def __init__(self, uri, segments):
        self._uri = uri
        self._segments = tuple(segments)

    def __str__(self):
        if self._uri is None:
            return self.path
        return str(self.uri) + self.path

    @property
    def uri(self):
        return self._uri

    @property
    def scheme(self):
        if self._uri is None:
            return None
        return self._uri.scheme

    @property
    def location(self):
        if self._uri is None:
            return None
        return self._uri.location

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
    """
    """
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
        try:
            uri = parse_systemuri(segments[0])
        except:
            raise Exception("invalid proberef %s: uri part is malformed" % string)
    # parse each segment in path
    path = list()
    for segment in segments[1:]:
        segment = segment.strip()
        if segment == '':
            raise Exception("invalid proberef %s: empty path segment is not allowed" % string)
        path.append(segment)
    return ProbeRef(uri, path)
