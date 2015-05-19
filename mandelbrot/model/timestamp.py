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

UTC = datetime.timezone(datetime.timedelta(0), 'Z')

class Timestamp(StructuredMixin):
    """
    """
    def __init__(self):
        self.datetime = None

    def get_datetime(self):
        return self.datetime

    def set_datetime(self, value):
        assert isinstance(value, datetime.datetime)
        assert value.tzinfo.utcoffset(None).total_seconds() == 0.0
        self.datetime = value

    def destructure(self):
        return int(self.datetime.timestamp() * 1000.0)

def _construct_timestamp(structure):
    assert isinstance(structure, int)
    dt = datetime.datetime.fromtimestamp(structure / 1000.0, UTC)
    timestamp = Timestamp()
    timestamp.set_datetime(dt)
    return timestamp

add_constructor(Timestamp, _construct_timestamp)

def now():
    timestamp = Timestamp()
    timestamp.set_datetime(datetime.datetime.now(UTC))
    return timestamp

def timestamp(*args, **kwargs):
    timestamp = Timestamp()
    timestamp.set_datetime(datetime.datetime(*args, **kwargs).astimezone(UTC))
    return timestamp
