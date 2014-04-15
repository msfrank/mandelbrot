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

from collections import MutableMapping

class MBObject(MutableMapping):
    """
    """
    def __init__(self):
        self.parent = None
        self.children = dict()

    def __getitem__(self, name):
        return self.children[name]

    def __setitem__(self, name, mbobject):
        if not isinstance(mbobject, MBObject):
            raise TypeError()
        if mbobject.parent is not None:
            raise RuntimeError()
        self.children[name] = mbobject
        mbobject.parent = self

    def __delitem__(self, name):
        raise RuntimeError()

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)
