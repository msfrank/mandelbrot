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

import os
from pesky.settings import ConfigureError
from twisted.persisted.dirdbm import DirDBM
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.state')

class StateDatabase(object):
    """
    Persists state on the filesystem.
    """
    def __init__(self, path):
        path = os.path.abspath(path)
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise Exception("path %s exists but is not a directory" % path)
        else:
            try:
                os.mkdir(path)
            except Exception, e:
                raise Exception("failed to create state directory %s" % path)
        self._db = DirDBM(path) 
        logger.debug("reading state from " + path)

    def get(self, name, default=None):
        return self._db.get(name, default)

    def put(self, name, value):
        self._db[name] = value

    def clear(self):
        self._db.clear()

    def last_modified(self, name):
        return self._db.getModificationTime(name)
