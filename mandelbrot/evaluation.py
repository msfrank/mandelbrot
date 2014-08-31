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

import time

class Health(object):
    HEALTHY  = 'healthy'
    DEGRADED = 'degraded'
    FAILED   = 'failed'
    UNKNOWN  = 'unknown'

    def __init__(self, health, summary, timestamp=None):
        self.health = health
        self.summary = summary
        self.timestamp = timestamp

class Metrics(object):
    def __init__(self, metrics, timestamp=None):
        self.metrics = metrics
        self.timestamp = timestamp

class Evaluation(object):
    """
    """
    def __init__(self, health=None, metrics=None, timestamp=None):
        self.health = health
        self.metrics = metrics
        self._timestamp = timestamp if timestamp is not None else time.time()

    @property
    def timestamp(self):
        return long(self._timestamp * 1000.0)
