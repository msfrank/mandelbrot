import asyncio
import urllib.parse
import requests
import logging

log = logging.getLogger("mandelbrot.endpoint")

import mandelbrot

class Endpoint(object):
    """
    """
    def __init__(self, event_loop, base_url, session, executor):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param base_url:
        :type base_url: str
        :param session:
        :type session: requests.Session
        :param executor:
        :type executor: concurrent.futures.Executor
        """
        self.event_loop = event_loop
        urlparts = urllib.parse.urlparse(base_url)
        self.scheme = urlparts.scheme
        self.netloc = urlparts.netloc
        self.session = session
        self.executor = executor
        self.session.headers = {
            'accept': 'application/json',
            'user-agent': "mandelbrot " + mandelbrot.versionstring(),
            }

    def absolute_url(self, path):
        return urllib.parse.urlunparse((self.scheme, self.netloc, path, '', '', ''))

    def request(self, request, processor):
        """
        :param request:
        :type request: requests.Request
        :returns: The Response object wrapped in a Future.
        :rtype: asyncio.Future
        """
        def send_request():
            try:
                prepared = self.session.prepare_request(request)
                response = self.session.send(prepared)
                if response.status_code >= 400:
                    return Failure(response, None)
                return processor(response)
            except Exception as e:
                return Failure(None, e)
        return self.event_loop.run_in_executor(self.executor, send_request)

    def request_item(self, request, constructor):
        """
        :param request:
        :type request: requests.Request
        :param constructor:
        :type constructor: callable
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future
        """
        def processor(response):
            return ResponseItem(response, constructor(response.json()))
        return self.request(request, processor)

    def request_response(self, request):
        """
        :param request:
        :type request: requests.Request
        :param constructor:
        :type constructor: callable
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future
        """
        def processor(response):
            return response
        return self.request(request, processor)

class ResponseItem(object):
    """
    """
    def __init__(self, response, item):
        self.response = response
        self.item = item

class Failure(object):
    def __init__(self, response, exception):
        self.response = response
        self.exception = exception
    def __repr__(self):
        if self.exception is not None:
            return "Failure({0})".format(str(self.exception))
        if self.response is not None:
            return "Failure({0})".format(str(self.response))
        return str(self)

class EndpointException(Exception):
    pass

class BadRequest(EndpointException):
    pass

class Conflict(EndpointException):
    pass

class Forbidden(EndpointException):
    pass

class InternalError(EndpointException):
    pass

class NotImplemented(EndpointException):
    pass

class ResourceNotFound(EndpointException):
    pass

class RetryLater(EndpointException):
    pass