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

import datetime

class MetricSource(object):
    """
    """
    def __init__(self, probepath, metricname):
        self.probepath = probepath
        self.metricname = metricname
    def __str__(self):
        return self.probepath + ":" + self.metricname
    def __repr__(self):
        return str(self)

class MetricUnit:
    UNITS = 'units'
    OPS = 'operations'
    PERCENT = 'percent'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
    MILLISECONDS = 'milliseconds'
    MICROSECONDS = 'microseconds'
    BYTES = 'bytes'
    KILOBYTES = 'kilobytes'
    MEGABYTES = 'megabytes'
    GIGABYTES = 'gigabytes'
    TERABYTES = 'terabytes'

class SourceType:
    GAUGE = 'gauge'
    COUNTER = 'counter'

class Consolidate:
    LAST = 'last'
    FIRST = 'first'
    MIN = 'min'
    MAX = 'max'
    MEAN = 'mean'

class Metric(object):
    """
    """
    def __init__(self, sourcetype, unit, step=None, heartbeat=None, cf=None):
        self.sourcetype = sourcetype
        self.unit = unit
        self.step = step
        self.heartbeat = heartbeat
        self.cf = cf
