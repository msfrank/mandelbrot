import asyncio

entry_point_type = 'mandelbrot.transport'

class Transport(object):
    """
    """
    def __init__(self, url, event_loop, executor, **kwargs):
        """
        :param url:
        :type url: urllib.parse.ParseResult
        :param event_loop: 
        :type event_loop: asyncio.AbstractEventLoop
        :param executor:
        :type executor: concurrent.futures.Executor
        """
        self.url = url
        self.event_loop = event_loop
        self.executor = executor

    @asyncio.coroutine
    def create_item(self, path, item):
        """
        Create a new item in the collection specified by path.  If the
        item exists, raises Conflict.

        :param path:
        :type path: str
        :param item:
        :type item: dict
        :raises BadRequest:
        :raises Conflict:
        :raises Forbidden:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def replace_item(self, path, item):
        """
        Replace the existing item at path with the specified item.  If the
        item doesn't exist, raises ResourceNotFound.

        :param path:
        :type path: str
        :param item:
        :type item: dict
        :raises BadRequest:
        :raises ResourceNotFound:
        :raises Forbidden:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def delete_item(self, path):
        """
        Delete the existing item at path.  If the item doesn't exist,
        raises ResourceNotFound.

        :param path:
        :type path: str
        :raises BadRequest:
        :raises ResourceNotFound:
        :raises Forbidden:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def get_item(self, path, filters):
        """
        Retrieve the existing item at path and filter the result.  If the
        item doesn't exist, raisesw ResourceNotFound.

        :param path:
        :type path: str
        :param filters:
        :type filters dict
        :raises BadRequest:
        :raises ResourceNotFound:
        :raises Forbidden:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def patch_item(self, path, fields, constraints):
        """
        Conditionally replace the specified fields for the item at the
        specified path, if all constraints hold.

        :param path:
        :type path: str
        :param fields:
        :type fields: dict
        :param constraints:
        :type constraints: dict
        :raises BadRequest:
        :raises Conflict:
        :raises ResourceNotFound:
        :raises Forbidden:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def get_collection(self, path, matchers, count, last):
        """
        Retrieve items in the specified collection.  If matchers is specified,
        then only retrieve items which match the specified constraints.  if
        count is specified, then return no more than the specified number of
        items.

        :param path:
        :type path: str
        :param matchers:
        :type matchers: dict
        :param count:
        :type count: int
        :param last:
        :type last: str
        :rtype: Page
        :raises BadRequest:
        :raises ResourceNotFound:
        :raises Forbidden:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def delete_collection(self, path, params):
        """
        :raises BadRequest:
        :raises ResourceNotFound:
        :raises Forbidden:
        """
        raise NotImplementedError()

    def close(self):
        """
        Release resources associated with the transport.
        """
        pass

class TransportException(Exception):
    """
    """

class BadRequest(TransportException):
    pass

class Conflict(TransportException):
    pass

class Forbidden(TransportException):
    pass

class InternalError(TransportException):
    pass

class NotImplemented(TransportException):
    pass

class ResourceNotFound(TransportException):
    pass

class RetryLater(TransportException):
    pass
