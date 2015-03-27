import asyncio
import concurrent.futures
import urllib.parse
import requests
import logging

log = logging.getLogger("mandelbrot.agent.endpoint")

import mandelbrot

class Endpoint(object):
    """
    """
    def __init__(self, event_loop, base_url, pool_size, session):
        """
        :param event_loop:
        :type event_loop: asyncio.BaseEventLoop
        :param host_name:
        :type host_name: str
        :param pool_size:
        :type pool_size: int
        :param session:
        :type session: requests.Session
        """
        self.event_loop = event_loop
        urlparts = urllib.parse.urlparse(base_url)
        self.scheme = urlparts.scheme
        self.netloc = urlparts.netloc
        self.pool_size = pool_size
        self.session = session
        self.executor = concurrent.futures.ThreadPoolExecutor(pool_size)
        self.session.headers = {
            'accept': 'application/json',
            'user-agent': "mandelbrot " + mandelbrot.versionstring(),
            }

    def absolute_url(self, path):
        return urllib.parse.urlunparse((self.scheme, self.netloc, path, '', '', ''))

    def request(self, request, constructor):
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
                data = response.json()
                if constructor is not None:
                    data = constructor(data)
                return ResponseItem(response, data)
            except Exception as e:
                return Failure(None, e)
        return self.event_loop.run_in_executor(self.executor, send_request)

    def request_item(self, request, constructor=None):
        """
        :param request:
        :type request: requests.Request
        :param constructor:
        :type constructor: callable
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future
        """
        request_future = self.request(request, constructor)
        future = asyncio.Future(loop=self.event_loop)
        def construct(_request_future):
            log.debug("request_future: %s", _request_future)
            future.set_result(_request_future.result())
        request_future.add_done_callback(construct)
        return future

    def get_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='GET',
            url=self.absolute_url('v2/systems/' + agent_id)
            )
        return self.request_item(request)

    def register_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='POST', url=self.absolute_url('v2/systems'),
            json=registration.destructure())
        return self.request_item(request)

    def update_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='PUT',
            url=self.absolute_url('v2/systems/' + agent_id),
            json=registration.destructure())
        return self.request_item(request)

    def unregister_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='DELETE',
            url=self.absolute_url('v2/systems/' + agent_id),
            )
        return self.request_item(request)

    def submit_evaluation(self, agent_id, evaluation):
        """
        """
        raise NotImplementedError()

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