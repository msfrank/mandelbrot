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
from mandelbrot.ref import parse_systemuri
from mandelbrot.http import http, as_json, from_json
from mandelbrot.timerange import parse_timerange
from mandelbrot.table import sort_results, render_table
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG

logger = getLogger('mandelbrot.client.system')

from mandelbrot.table import millis2ctime, bool2checkbox
renderers = {
    'lastChange': millis2ctime,
    'lastUpdate': millis2ctime,
    'timestamp':  millis2ctime,
    'squelched':  bool2checkbox,
}

def system_status_callback(ns):
    """
    """
    # client settings
    section = ns.get_section('client')
    server = section.get_str('host')
    # client:system:history settings
    section = ns.get_section('client:system:status')
    fields = ('probeRef','lifecycle','health','summary','timestamp','lastChange','lastUpdate','squelched')
    fields = section.get_list('status fields', fields)
    sort = section.get_list('status sort', ['probeRef'])
    tablefmt = section.get_str('status table format', 'simple')
    (system,) = ns.get_args(parse_systemuri, minimum=1, names=('URI',))
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    url = urljoin(server, 'objects/systems/' + str(system) + '/properties/status')
    logger.debug("connecting to %s", url)
    defer = http.agent(timeout=3).request('GET', url)
    def onbody(body, code):
        logger.debug("received body %s", body)
        if code == 200:
            status = sort_results(from_json(body), sort)
            print render_table(status, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        else:
            print "error: " + from_json(body)['description']
        reactor.stop()
    def onfailure(failure):
        logger.debug("query failed: %s", failure.getErrorMessage())
        reactor.stop()
    def onresponse(response):
        logger.debug("received response %i %s", response.code, response.phrase)
        http.read_body(response).addCallbacks(onbody, onfailure, callbackArgs=(response.code,))
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()

def system_history_callback(ns):
    """
    """
    # client settings
    section = ns.get_section('client')
    server = section.get_str('host')
    # client:system:history settings
    section = ns.get_section('client:system:history')
    timerange = section.get_str('history timerange')
    limit = section.get_int('history limit')
    fields = ('timestamp', 'probeRef','lifecycle','health','summary','lastChange','lastUpdate','squelched')
    fields = section.get_list('history fields', fields)
    sort = section.get_list('history sort', ['timestamp'])
    tablefmt = section.get_str('history table format', 'simple')
    (system,) = ns.get_args(parse_systemuri, minimum=1, names=('URI'))
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    # build query url
    params = list()
    if timerange is not None:
        start,end = parse_timerange(timerange)
        if start is not None:
            params.append(('from', calendar.timegm(start.utctimetuple())))
        if end is not None:
            params.append(('to', calendar.timegm(end.utctimetuple())))
    if limit is not None:
        params.append(('limit', limit))
    qs = urlencode(params)
    url = urlparse(urljoin(server, 'objects/systems/' + str(system) + '/collections/history?' + qs))
    # execute query
    logger.debug("connecting to %s://%s", url.scheme, url.netloc)
    logger.debug("GET %s?%s", url.path, url.query)
    defer = http.agent(timeout=3).request('GET', url.geturl())
    def onbody(body):
        logger.debug("received body %s", body)
        history = sort_results(from_json(body), sort)
        print render_table(history, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
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
    # client settings
    section = ns.get_section('client')
    server = section.get_str('host')
    # client:system:notifications settings
    section = ns.get_section('client:system:notifications')
    timerange = section.get_str('notifications timerange')
    limit = section.get_int('notifications limit')
    fields = ('timestamp', 'probeRef', 'description', 'correlation')
    fields = section.get_list('notifications fields', fields)
    sort = section.get_list('notifications sort', ['timestamp'])
    tablefmt = section.get_str('notifications table format', 'simple')
    (system,) = ns.get_args(parse_systemuri, minimum=1, names=('URI'))
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    # build query url
    url = urljoin(server, 'objects/systems/' + str(system) + '/collections/notifications')
    # execute query
    logger.debug("connecting to %s", url)
    defer = http.agent(timeout=3).request('GET', url)
    def onbody(body):
        logger.debug("received body %s", body)
        notifications = sort_results(from_json(body), sort)
        print render_table(notifications, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        reactor.stop()
    def onfailure(failure):
        logger.debug("query failed: %s", failure.getErrorMessage())
        reactor.stop()
    def onresponse(response):
        logger.debug("received response %i %s", response.code, response.phrase)
        http.read_body(response).addCallbacks(onbody, onfailure)
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()
    
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
                         Option('f', 'fields', 'status fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'status sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
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
                         Option('T', 'table-format', 'history table format', help="display result using the specified FMT", metavar="FMT")
                       ],
                       callback=system_history_callback),
                     Action("notifications",
                       usage="[OPTIONS] REF",
                       description="get notifications for REF",
                       options=[
                         Option('t', 'range', 'notifications timerange', help="retrieve notifications within the specified TIMERANGE", metavar="TIMERANGE"),
                         Option('l', 'limit', 'notifications limit', help="return a maximum of LIMIT results", metavar="LIMIT"),
                         Option('f', 'fields', 'notifications fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'notifications sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('T', 'table-format', 'table format', help="display result using the specified FMT", metavar="FMT")
                       ],
                       callback=system_notifications_callback),
                   ]
                 )
