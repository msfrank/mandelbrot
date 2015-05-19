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

import asyncio
import logging

log = logging.getLogger("mandelbrot.transport.dummy")

from mandelbrot.transport import *

class DummyTransport(Transport):
    """
    """
    @asyncio.coroutine
    def create_item(self, path, item):
        log.info("create item %s from %s", str(path), str(item))
        return None

    @asyncio.coroutine
    def replace_item(self, path, item):
        log.info("replace item %s with %s", str(path), str(item))
        return None

    @asyncio.coroutine
    def delete_item(self, path):
        log.info("delete item %s", str(path))
        return None

    @asyncio.coroutine
    def get_item(self, path, filters):
        log.info("get item %s filtering on %s", str(path), str(filters))
        raise NotImplementedError()

    @asyncio.coroutine
    def patch_item(self, path, fields, constraints):
        log.info("patch item %s with fields %s given constraints %s",
                 str(path), str(fields), str(constraints))
        raise NotImplementedError()

    @asyncio.coroutine
    def get_collection(self, path, matchers, count, last):
        log.info("get %d items from collection %s matching %s resuming from last item %s",
                 count, str(path), str(matchers), str(last))
        raise NotImplementedError()

    @asyncio.coroutine
    def delete_collection(self, path, params):
        log.info("delete items from collection %s matching params %s",
                 str(path), str(params))
        raise NotImplementedError()
