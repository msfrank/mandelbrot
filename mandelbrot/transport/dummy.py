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
