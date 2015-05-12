import asyncio

from mandelbrot.transport import *

class MockTransport(Transport):

    def mock_create_item(self, path, item):
        raise NotImplementedError()

    @asyncio.coroutine
    def create_item(self, path, item):
        return self.mock_create_item(path, item)

    def mock_replace_item(self, path, item):
        raise NotImplementedError()

    @asyncio.coroutine
    def replace_item(self, path, item):
        return self.mock_replace_item(path, item)

    def mock_delete_item(self, path):
        raise NotImplementedError()

    @asyncio.coroutine
    def delete_item(self, path):
        return self.mock_delete_item(path)

    def mock_get_item(self, path, filters):
        raise NotImplementedError()

    @asyncio.coroutine
    def get_item(self, path, filters):
        return self.mock_get_item(path, filters)

    def mock_patch_item(self, path, fields, constraints):
        raise NotImplementedError()

    @asyncio.coroutine
    def patch_item(self, path, fields, constraints):
        return self.mock_patch_item(path, fields, constraints)

    def mock_get_collection(self, path, matchers, count, last):
        raise NotImplementedError()

    @asyncio.coroutine
    def get_collection(self, path, matchers, count, last):
        return self.mock_get_collection(path, matchers, count, last)

    def mock_delete_collection(self, path, params):
        raise NotImplementedError()

    @asyncio.coroutine
    def delete_collection(self, path, params):
        return self.mock_delete_collection(path, params)
