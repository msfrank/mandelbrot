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

from mandelbrot.probes import IProbe

class SystemLoadLinux(IProbe):
    """
    """
    def configure(self, section):
        pass

    def probe(self):
        with open('/proc/loadavg', 'r') as f:
            fields = [field for field in f.readline().split(' ') if field != '']
            load1  = float(fields[0])
            load5  = float(fields[1])
            load15 = float(fields[2])
        with open('/proc/cpuinfo', 'r') as f:
            ncores = 0
            for line in f.readlines():
                name,value = line.split(':', 1)
                name = name.strip()
                value = value.lstrip()
                if name == 'processor':
                    ncores += 1