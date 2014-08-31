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

import collections, time

from mandelbrot.ref import parse_proberef

def millis2ctime(millis):
    return time.ctime(millis / 1000.0)

def timedelta2seconds(td):
    return (float(td.microseconds) + (float(td.seconds) + float(td.days) * 24.0 * 3600.0) * 10**6) / 10**6

def bool2checkbox(value):
    if value is False or value is None:
        return ""
    return "*"

def bool2string(value):
    if value is False or value is None:
        return "false"
    return "true"

def proberef2path(value):
    try:
        ref = parse_proberef(value)
        return ref.path
    except:
        return ""

def size2string(size):
    if size < 1024:
        return "%i bytes" % size
    if size < 1024 * 1024:
        return "%.1f kilobytes" % (float(size) / 1024.0)
    if size < 1024 * 1024 * 1024:
        return "%.1f megabytes" % (float(size) / (1024.0 * 1024.0))
    if size < 1024 * 1024 * 1024 * 1024:
        return "%.1f gigabytes" % (float(size) / (1024.0 * 1024.0 * 1024.0))
    if size < 1024 * 1024 * 1024 * 1024 * 1024:
        return "%.1f terabytes" % (float(size) / (1024.0 * 1024.0 * 1024.0 * 1024.0))
    if size < 1024 * 1024 * 1024 * 1024 * 1024 * 1024:
        return "%.1f petabytes" % (float(size) / (1024.0 * 1024.0 * 1024.0 * 1024.0 * 1024.0))

def list2csv(values):
    return ", ".join(values)

def list2nsv(values):
    return "\n".join(values)
