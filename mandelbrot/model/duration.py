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

import datetime

from mandelbrot.model import StructuredMixin, add_constructor

class Duration(StructuredMixin):
    """
    """
    def __init__(self):
        self.timedelta = None

    def get_timedelta(self):
        return self.timedelta

    def set_timedelta(self, value):
        assert isinstance(value, datetime.timedelta)
        self.timedelta = value

    def destructure(self):
        return int(self.timedelta / datetime.timedelta(milliseconds=1))

def _construct_duration(structure):
    assert isinstance(structure, int)
    td = datetime.timedelta(milliseconds=structure)
    duration = Duration()
    duration.set_timedelta(td)
    return duration

add_constructor(Duration, _construct_duration)
