import asyncio
import concurrent.futures
import contextlib
import logging

log = logging.getLogger("mandelbrot.query.endpoint")

from mandelbrot.model import construct
from mandelbrot.model.registration import Registration
from mandelbrot.model.agent_metadata import AgentMetadataPage
from mandelbrot.model.check_condition import CheckCondition, CheckConditionPage
from mandelbrot.model.check_notifications import CheckNotifications, CheckNotificationsPage
from mandelbrot.model.check_metrics import CheckMetrics, CheckMetricsPage
from mandelbrot.model.timestamp import Timestamp
from mandelbrot.transport import Transport, entry_point_type

class Endpoint(object):
    """
    """
    def __init__(self, transport):
        """
        :param transport:
        :type transport: mandelbrot.transport.Transport
        """
        self.transport = transport

    @asyncio.coroutine
    def list_agents(self, count, last):
        """
        """
        path = 'v2/agents'
        agents_page = yield from self.transport.get_collection(path, {}, count, last)
        return construct(AgentMetadataPage, agents_page)

    @asyncio.coroutine
    def get_agent_registration(self, agent_id):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :returns: The current agent registration
        :rtype: Registration
        """
        path = 'v2/agents/' + str(agent_id)
        registration = yield from self.transport.get_item(path, {})
        return construct(Registration, registration)

    @asyncio.coroutine
    def get_current_condition(self, agent_id, check_id):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :returns: The current check condition
        :rtype: CheckCondition
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id) + '/condition'
        page = yield from self.transport.get_collection(path, {}, count=1, last=None)
        check_condition_page = construct(CheckConditionPage, page)
        return check_condition_page.check_conditions[0]

    @asyncio.coroutine
    def list_conditions(self, agent_id, check_id, limit, start=None, end=None,
                        last=None, start_inclusive=False, end_exclusive=False,
                        descending=False):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :param limit:
        :type limit: int
        :param last:
        :type last: str
        :param start_inclusive:
        :type start_inclusive: bool
        :param end_exclusive:
        :type end_exclusive: bool
        :param descending:
        :type descending: bool
        :returns: The check conditions matching the specified parameters
        :rtype: CheckConditionPage
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id) + '/condition'
        matchers = {}
        if start:
            assert isinstance(start, Timestamp)
            matchers['from'] = start
        if end:
            assert isinstance(end, Timestamp)
            matchers['to'] = end
        if start_inclusive:
            assert isinstance(start_inclusive, bool)
            matchers['fromInclusive'] = start_inclusive
        if end_exclusive:
            assert isinstance(end_exclusive, bool)
            matchers['toExclusive'] = end_exclusive
        if descending:
            assert isinstance(descending, bool)
            matchers['descending'] = descending
        page = yield from self.transport.get_collection(path, matchers, count=limit, last=last)
        return construct(CheckConditionPage, page)

    @asyncio.coroutine
    def get_current_notifications(self, agent_id, check_id):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :returns: The current check notifications
        :rtype: CheckNotifications
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id) + '/notifications'
        page = yield from self.transport.get_collection(path, {}, count=1, last=None)
        check_notifications_page = construct(CheckNotificationsPage, page)
        return check_notifications_page.list_check_notifications()[0]

    @asyncio.coroutine
    def list_notifications(self, agent_id, check_id, limit, start=None, end=None,
                           last=None, start_inclusive=False, end_exclusive=False,
                           descending=False):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :param limit:
        :type limit: int
        :param last:
        :type last: str
        :param start_inclusive:
        :type start_inclusive: bool
        :param end_exclusive:
        :type end_exclusive: bool
        :param descending:
        :type descending: bool
        :returns: The check notifications matching the specified parameters
        :rtype: CheckNotificationsPage
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id) + '/notifications'
        matchers = {}
        if start:
            assert isinstance(start, Timestamp)
            matchers['from'] = start
        if end:
            assert isinstance(end, Timestamp)
            matchers['to'] = end
        if start_inclusive:
            assert isinstance(start_inclusive, bool)
            matchers['fromInclusive'] = start_inclusive
        if end_exclusive:
            assert isinstance(end_exclusive, bool)
            matchers['toExclusive'] = end_exclusive
        if descending:
            assert isinstance(descending, bool)
            matchers['descending'] = descending
        page = yield from self.transport.get_collection(path, matchers, count=limit, last=last)
        return construct(CheckNotificationsPage, page)

    @asyncio.coroutine
    def get_current_metrics(self, agent_id, check_id):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :returns: The current check metrics
        :rtype: CheckMetrics
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id) + '/metrics'
        page = yield from self.transport.get_collection(path, {}, count=1, last=None)
        check_metrics_page = construct(CheckMetricsPage, page)
        return check_metrics_page.list_check_metrics()[0]

    @asyncio.coroutine
    def list_metrics(self, agent_id, check_id, limit, start=None, end=None,
                     last=None, start_inclusive=False, end_exclusive=False,
                     descending=False):
        """
        :param agent_id:
        :type agent_id: cifparser.Path
        :param check_id:
        :type check_id: cifparser.Path
        :param limit:
        :type limit: int
        :param last:
        :type last: str
        :param start_inclusive:
        :type start_inclusive: bool
        :param end_exclusive:
        :type end_exclusive: bool
        :param descending:
        :type descending: bool
        :returns: The check metrics matching the specified parameters
        :rtype: CheckMetricsPage
        """
        path = 'v2/agents/' + str(agent_id) + '/checks/' + str(check_id) + '/metrics'
        matchers = {}
        if start:
            assert isinstance(start, Timestamp)
            matchers['from'] = start
        if end:
            assert isinstance(end, Timestamp)
            matchers['to'] = end
        if start_inclusive:
            assert isinstance(start_inclusive, bool)
            matchers['fromInclusive'] = start_inclusive
        if end_exclusive:
            assert isinstance(end_exclusive, bool)
            matchers['toExclusive'] = end_exclusive
        if descending:
            assert isinstance(descending, bool)
            matchers['descending'] = descending
        page = yield from self.transport.get_collection(path, matchers, count=limit, last=last)
        return construct(CheckMetricsPage, page)

@contextlib.contextmanager
def make_endpoint(event_loop, endpoint_url, registry, transport_workers):
    """
    Create the transport and construct the agent endpoint.

    :param event_loop:
    :type event_loop: asyncio.AbstractEventLoop
    :param endpoint_url:
    :type endpoint_url: urllib.parse.ParseResult
    :param registry:
    :type registry: mandelbrot.registry.Registry
    :param num_workers:
    :type num_workers: int
    :return:
    """
    transport_factory = registry.lookup_factory(entry_point_type,
        endpoint_url.scheme, Transport)
    transport_executor = concurrent.futures.ThreadPoolExecutor(transport_workers)
    transport = transport_factory(endpoint_url, event_loop, transport_executor)
    log.debug("instantiating %s transport for %s", endpoint_url.scheme, endpoint_url)
    yield Endpoint(transport)
    transport.close()
    transport_executor.shutdown()
