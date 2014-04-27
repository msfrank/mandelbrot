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

import collections, calendar
from urllib import urlencode
from urlparse import urlparse, urljoin
from twisted.internet import reactor
from tabulate import tabulate
from mandelbrot.http import http, as_json, from_json
from mandelbrot.timerange import parse_timerange
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG

logger = getLogger('mandelbrot.client.system')

def system_status_callback(ns):
    """
    """
    section = ns.get_section('client')
    server = section.get_str('host')
    tablefmt = section.get_str('table format', 'simple')
    (ref,) = ns.get_args(str, minimum=1, names=('REF'))
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    url = urljoin(server, 'objects/systems/' + ref + '/properties/status')
    logger.debug("connecting to %s", url)
    defer = http.agent(timeout=3).request('GET', url)
    def onbody(body):
        logger.debug("received body %s", body)
        states = from_json(body)
        table = collections.OrderedDict()
        table['probeRef'] = []
        table['lifecycle'] = []
        table['health'] = []
        table['summary'] = []
        table['lastChange'] = []
        table['lastUpdate'] = []
        table['squelched'] = []
        for state in sorted(states, key=lambda s: s['probeRef']):
            for name,column in table.items():
                if name in state:
                    column.append(state[name])
                else:
                    column.append(None)
        print tabulate(table, headers='keys', tablefmt=tablefmt)
        reactor.stop()
    def onfailure(failure):
        logger.debug("query failed: %s", failure.getErrorMessage())
        reactor.stop()
    def onresponse(response):
        logger.debug("received response %i %s", response.code, response.phrase)
        http.read_body(response).addCallbacks(onbody, onfailure)
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()

def system_history_callback(ns):
    """
    """
    section = ns.get_section('client')
    server = section.get_str('host')
    timerange = section.get_str('history timerange')
    limit = section.get_int('history limit')
    #fields = section.get_list('history fields')
    #sort = section.get_list('history sort'
    #columns = section.get_list('history columns')
    tablefmt = section.get_str('table format', 'simple')
    (ref,) = ns.get_args(str, minimum=1, names=('REF'))
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    # build query params
    params = list()
    if timerange is not None:
        start,end = parse_timerange(timerange)
        if start is not None:
            params.append(('from', calendar.timegm(start.utctimetuple())))
        if end is not None:
            params.append(('to', calendar.timegm(end.utctimetuple())))
    if limit is not None:
        params.append(('limit', limit))
    #
    qs = urlencode(params)
    url = urlparse(urljoin(server, 'objects/systems/' + ref + '/collections/history?' + qs))
    logger.debug("connecting to %s://%s", url.scheme, url.netloc)
    logger.debug("GET %s?%s", url.path, url.query)
    defer = http.agent(timeout=3).request('GET', url.geturl())
    def onbody(body):
        logger.debug("received body %s", body)
        states = from_json(body)
        table = collections.OrderedDict()
        table['probeRef'] = []
        table['lifecycle'] = []
        table['health'] = []
        table['summary'] = []
        table['lastChange'] = []
        table['lastUpdate'] = []
        table['squelched'] = []
        for state in sorted(states, key=lambda s: s['probeRef']):
            for name,column in table.items():
                if name in state:
                    column.append(state[name])
                else:
                    column.append(None)
        print tabulate(table, headers='keys', tablefmt=tablefmt)
        reactor.stop()
    def onfailure(failure):
        logger.debug("query failed: %s", failure.getErrorMessage())
        reactor.stop()
    def onresponse(response):
        logger.debug("received response %i %s", response.code, response.phrase)
        http.read_body(response).addCallbacks(onbody, onfailure)
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()

def system_notifications_callback(ns):
    """
    """
    section = ns.get_section('client')
    server = section.get_str('host')
    tablefmt = section.get_str('table format', 'simple')
    (ref,) = ns.get_args(str, minimum=1, names=('REF'))
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    url = urljoin(server, 'objects/systems/' + ref + '/collections/notifications')
    logger.debug("connecting to %s", url)
    defer = http.agent(timeout=3).request('GET', url)
    def onbody(body):
        logger.debug("received body %s", body)
        states = from_json(body)
        table = collections.OrderedDict()
        table['probeRef'] = []
        table['timestamp'] = []
        table['description'] = []
        table['correlation'] = []
        for state in sorted(states, key=lambda s: s['probeRef']):
            for name,column in table.items():
                if name in state:
                    column.append(state[name])
                else:
                    column.append(None)
        print tabulate(table, headers='keys', tablefmt=tablefmt)
        reactor.stop()
    def onfailure(failure):
        logger.debug("query failed: %s", failure.getErrorMessage())
        reactor.stop()
    def onresponse(response):
        logger.debug("received response %i %s", response.code, response.phrase)
        http.read_body(response).addCallbacks(onbody, onfailure)
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()
    
def system_acknowledge_callback(ns):
    pass

def system_squelch_callback(ns):
    pass

def system_unsquelch_callback(ns):
    pass

from pesky.settings.action import Action, NOACTION
from pesky.settings.option import *

system_actions = Action("system",
                   usage="COMMAND",
                   description="Interact with systems in a Mandelbrot cluster",
                   callback=NOACTION,
                   actions=[
                     Action("status",
                       usage="[OPTIONS] REF",
                       description="get the current status of REF",
                       options=[
                         Option('T', 'table-format', 'status table format', help="display result using the specified FMT", metavar="FMT")
                         ],
                       callback=system_status_callback),
                     Action("history",
                       usage="[OPTIONS] REF...",
                       description="get status history for REF",
                       options=[
                         Option('t', 'range', 'history timerange', help="retrieve history within the specified TIMERANGE", metavar="TIMERANGE"),
                         Option('l', 'limit', 'history limit', help="return a maximum of LIMIT results", metavar="LIMIT"),
                         Option('f', 'fields', 'history fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'history sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('c', 'columns', 'history columns', help="place result columns in the order specified by COLUMNS", metavar="COLUMNS"),
                         Option('T', 'table-format', 'history table format', help="display result using the specified FMT", metavar="FMT")
                       ],
                       callback=system_history_callback),
                     Action("notifications",
                       usage="[OPTIONS] REF",
                       description="get notifications for REF",
                       options=[
                         Option('T', 'table-format', 'table format', help="display result using the specified FMT", metavar="FMT")
                       ],
                       callback=system_notifications_callback),
                     Action("acknowledge",
                       usage="[OPTIONS] REF",
                       description="acknowledge REF",
                       options=[
                         Option('m', 'message', 'message', help="Use the given MESSAGE as the acknowledgement message", metavar="MESSAGE"),
                         ],
                       callback=system_acknowledge_callback),
                     Action("disable",
                       usage="[OPTIONS] REF",
                       description="disable notifications for REF",
                       options=[],
                       callback=system_squelch_callback),
                     Action("enable",
                       usage="[OPTIONS] REF",
                       description="enable notifications for REF",
                       options=[],
                       callback=system_unsquelch_callback),
                   ]
                 )
