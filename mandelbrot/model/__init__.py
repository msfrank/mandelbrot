# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
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

class StructuredMixin(object):
    """
    """
    def destructure(self):
        raise NotImplementedError()
    def __str__(self):
        return pprint.pformat(self.destructure(), indent=4)
    def __repr__(self):
        return str(self)

class SealedException(Exception):
    """
    """
    def __init__(self, obj, field):
        self.obj = obj
        self.field = field
    def __str__(self):
        return "failed to set field '{}': object is sealed".format(self.field)
    def __repr__(self):
        return str(self)

class SealableMixin(object):
    """
    """
    def seal(self):
        self.__setattr__ = self.__sealed

    def __sealed(self, key, value):
        raise SealedException(self, key)

_constructors = {}

def add_constructor(model_class, constructor):
    _constructors[model_class] = constructor

def construct(model_class, structure):
    """

    :param model_class:
    :type model_class: type
    :param structure:
    :type structure: object
    :return:
    """
    assert isinstance(model_class, type)
    try:
        factory = _constructors[model_class]
        return factory(structure)
    except KeyError:
        raise TypeError("don't know how to construct for type {}".format(model_class.__name__))


__all__ = [ 'construct' ]
