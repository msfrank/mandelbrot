import asyncio
import urllib.parse
import requests
import logging

log = logging.getLogger("mandelbrot.transport.http")

from mandelbrot import versionstring
from mandelbrot.transport import *

class HttpTransport(Transport):
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
        super().__init__(url, event_loop, executor)
        self.event_loop = event_loop
        self.scheme = self.url.scheme
        self.netloc = self.url.netloc
        if 'session' in kwargs:
            self.session = kwargs['session']
        else:
            self.session = requests.Session()
        self.session.headers = {
            'accept': 'application/json',
            'user-agent': "mandelbrot " + versionstring(),
            }

    def absolute_url(self, path):
        return urllib.parse.urlunparse((self.scheme, self.netloc, path, '', '', ''))

    def request(self, request):
        """
        :param request:
        :type request: requests.Request
        :returns: The Response object wrapped in a Future.
        :rtype: asyncio.Future
        """
        def send_request():
            prepared = self.session.prepare_request(request)
            response = self.session.send(prepared)
            try:
                if response.status_code == 400:
                    raise BadRequest()
                if response.status_code == 403:
                    raise Forbidden()
                if response.status_code == 404:
                    raise ResourceNotFound()
                if response.status_code == 409:
                    raise Conflict()
                if response.status_code == 500:
                    raise InternalError()
                if response.status_code == 501:
                    raise NotImplemented()
                if response.status_code == 503:
                    raise RetryLater()
                return response
            except Exception:
                self.log_response_and_entity(response)
                raise
        return self.event_loop.run_in_executor(self.executor, send_request)

    def log_response(self, response):
        request = response.request
        log.debug("%s %s returns %d %s", request.method,
            request.url, response.status_code, response.reason)

    def log_response_and_entity(self, response):
        request = response.request
        log.debug("%s %s returns %d %s:\n%s", request.method,
            request.url, response.status_code, response.reason, response.text)

    @asyncio.coroutine
    def create_item(self, path, item):
        request = requests.Request(
            method='POST', url=self.absolute_url(path), json=item)
        response = yield from self.request(request)
        try:
            entity = response.json()
        except ValueError:
            self.log_response(response)
        else:
            self.log_response_and_entity(response)
            return entity

    @asyncio.coroutine
    def replace_item(self, path, item):
        request = requests.Request(
            method='PUT', url=self.absolute_url(path), json=item)
        response = yield from self.request(request)
        try:
            entity = response.json()
        except ValueError:
            self.log_response(response)
        else:
            self.log_response_and_entity(response)
            return entity

    @asyncio.coroutine
    def delete_item(self, path):
        request = requests.Request(
            method='DELETE', url=self.absolute_url(path))
        response = yield from self.request(request)
        try:
            entity = response.json()
        except ValueError:
            self.log_response(response)
        else:
            self.log_response_and_entity(response)
            return entity

    @asyncio.coroutine
    def get_item(self, path, filters):
        request = requests.Request(
            method='GET', url=self.absolute_url(path), params=filters)
        response = yield from self.request(request)
        try:
            entity = response.json()
        except ValueError:
            self.log_response(response)
        else:
            self.log_response_and_entity(response)
            return entity

    @asyncio.coroutine
    def patch_item(self, path, fields, constraints):
        raise NotImplementedError()

    @asyncio.coroutine
    def get_collection(self, path, matchers, count, last):
        params = matchers.copy()
        if count is not None:
            params['limit'] = count
        if last is not None:
            params['last'] = last
        request = requests.Request(
            method='GET', url=self.absolute_url(path), params=params)
        response = yield from self.request(request)
        try:
            entity = response.json()
        except ValueError:
            self.log_response(response)
        else:
            self.log_response_and_entity(response)
            return entity

    @asyncio.coroutine
    def delete_collection(self, path, params):
        raise NotImplementedError()
