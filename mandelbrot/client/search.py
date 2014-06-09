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

from urllib import urlencode
from urlparse import urlparse, urljoin
from twisted.web.http_headers import Headers

from mandelbrot.client.action import action
from mandelbrot.ref import parse_systemuri, parse_proberef
from mandelbrot.http import http, as_json, from_json
from mandelbrot.timerange import parse_timerange
from mandelbrot.table import sort_results, render_table
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.client.search')

from mandelbrot.table import millis2ctime, bool2checkbox, proberef2path
renderers = {
    'lastChange': millis2ctime,
    'lastUpdate': millis2ctime,
    'timestamp':  millis2ctime,
    'acknowledged': bool2checkbox,
    'squelched':  bool2checkbox,
}

@action
def search_status_callback(ns):
    # client settings
    section = ns.get_section('client')
    search = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:search:history settings
    section = ns.get_section('client:search:status')
    fields = ('probeRef','lifecycle','health','acknowledged','summary','lastChange','lastUpdate','squelched')
    fields = section.get_list('status fields', fields)
    sort = section.get_list('status sort', ['probeRef'])
    tablefmt = section.get_str('status table format', 'simple')
    params = urlencode([('q', ' '.join(ns.get_args()))])
    # get the systems
    try:
        url = urljoin(search, 'services/status/search?' + params)
        logger.debug("connecting to %s", url)
        response = yield http.agent(timeout=3).request('GET', url)
        logger.debug("received response %i %s", response.code, response.phrase)
    except Exception, e:
        print "query failed: " + str(e)
        return
    # parse the response body
    try:
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code == 200:
            results = from_json(body).values()
            if len(results) > 0:
                status = sort_results(results, sort)
                print render_table(status, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        else:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "query failed: " + str(e)
        return


@action
def search_history_callback(ns):
    # client settings
    section = ns.get_section('client')
    search = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:search:history settings
    section = ns.get_section('client:search:history')
    timerange = section.get_str('history timerange')
    limit = section.get_int('history limit')
    fields = ('timestamp', 'probeRef','lifecycle','health','summary','lastChange','lastUpdate','squelched')
    fields = section.get_list('history fields', fields)
    sort = section.get_list('history sort', ['timestamp'])
    tablefmt = section.get_str('history table format', 'simple')
    params = [('q', ' '.join(ns.get_args()))]
    # build query url
    if timerange is not None:
        start,end = parse_timerange(timerange)
        if start is not None:
            params.append(('from', start.isoformat()))
        if end is not None:
            params.append(('to', end.isoformat()))
    if limit is not None:
        params.append(('limit', limit))
    qs = urlencode(params)
    # get the history
    try:
        url = urljoin(search, 'services/history/search?' + qs)
        logger.debug("connecting to %s", url)
        response = yield http.agent(timeout=3).request('GET', url)
        logger.debug("received response %i %s", response.code, response.phrase)
    except Exception, e:
        print "query failed: " + str(e)
        return
    # parse the response body
    try:
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code == 200:
            results = from_json(body)
            if len(results) > 0:
                history = sort_results(results, sort)
                print render_table(history, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        else:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "query failed: " + str(e)
        return


@action
def search_notifications_callback(ns):
    # client settings
    section = ns.get_section('client')
    search = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:search:notifications settings
    section = ns.get_section('client:search:notifications')
    timerange = section.get_str('notifications timerange')
    limit = section.get_int('notifications limit')
    fields = ('timestamp', 'probeRef', 'kind', 'description', 'correlation')
    fields = section.get_list('notifications fields', fields)
    sort = section.get_list('notifications sort', ['timestamp'])
    tablefmt = section.get_str('notifications table format', 'simple')
    params = [('q', ' '.join(ns.get_args()))]
    # build query url
    if timerange is not None:
        start,end = parse_timerange(timerange)
        if start is not None:
            params.append(('from', start.isoformat()))
        if end is not None:
            params.append(('to', end.isoformat()))
    if limit is not None:
        params.append(('limit', limit))
    qs = urlencode(params)
    # get the notifications
    try:
        url = urljoin(search, 'services/notifications/search?' + qs)
        logger.debug("connecting to %s", url)
        response = yield http.agent(timeout=3).request('GET', url)
        logger.debug("received response %i %s", response.code, response.phrase)
    except Exception, e:
        print "query failed: " + str(e)
        return
    # parse the response body
    try:
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code == 200:
            results = from_json(body)
            if len(results) > 0:
                notifications = sort_results(results, sort)
                print render_table(notifications, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        else:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "query failed: " + str(e)
        return


from pesky.settings.action import Action, NOACTION
from pesky.settings.option import *

search_actions = Action("search",
                   usage="COMMAND",
                   description="search Mandelbrot services",
                   callback=NOACTION,
                   actions=[
                     Action("status",
                       usage="[OPTIONS] QUERY",
                       description="retrieve status of all probes matching QUERY",
                       options=[
                         Option('f', 'fields', 'status fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'status sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('T', 'table-format', 'status table format', help="display result using the specified FMT", metavar="FMT")
                         ],
                       callback=search_status_callback),
                     Action("history",
                       usage="[OPTIONS] QUERY",
                       description="retrieve status history of all probes matching QUERY",
                       options=[
                         Option('t', 'range', 'history timerange', help="retrieve history within the specified TIMERANGE", metavar="TIMERANGE"),
                         Option('l', 'limit', 'history limit', help="return a maximum of LIMIT results", metavar="LIMIT"),
                         Option('f', 'fields', 'history fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'history sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('T', 'table-format', 'history table format', help="display result using the specified FMT", metavar="FMT")
                         ],
                       callback=search_history_callback),
                     Action("notifications",
                       usage="[OPTIONS] QUERY",
                       description="retrieve notification history of all probes matching QUERY",
                       options=[
                         Option('t', 'range', 'notifications timerange', help="retrieve history within the specified TIMERANGE", metavar="TIMERANGE"),
                         Option('l', 'limit', 'notifications limit', help="return a maximum of LIMIT results", metavar="LIMIT"),
                         Option('f', 'fields', 'notifications fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'notifications sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('T', 'table-format', 'notifications table format', help="display result using the specified FMT", metavar="FMT")
                         ],
                       callback=search_notifications_callback),
                     ]
                 )
