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

import sys

# load system defaults
try:
    from mandelbrot.defaults.system import defaults as system_defaults
    for name,value in system_defaults().items():
        setattr(sys.modules['mandelbrot.defaults'], name, value)
except Exception, e:
    pass

# load site overrides
try:
    from mandelbrot.defaults.site import defaults as site_defaults
    for name,value in defaults().items():
        setattr(sys.modules['mandelbrot.defaults'], name, value)
except Exception, e:
    pass
