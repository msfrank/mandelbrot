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
from mandelbrot.table import sort_results, render_table
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.client.server')

from mandelbrot.table import millis2ctime, list2csv
renderers = {
    'joinedOn': millis2ctime,
    'lastUpdate': millis2ctime,
    'from':  millis2ctime,
    'to':  millis2ctime,
    'affected': list2csv,
}

@action
def server_systems_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:system:history settings
    section = ns.get_section('client:server:systems')
    fields = ('uri','joinedOn','lastUpdate')
    fields = section.get_list('systems fields', fields)
    sort = section.get_list('systems sort', ['uri'])
    tablefmt = section.get_str('systems table format', 'simple')
    # get the systems
    try:
        url = urljoin(server, 'objects/systems')
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
            def makeresult(result):
                system = result[1]
                system['uri'] = result[0]
                return system
            results = map(makeresult, from_json(body).items())
            if len(results) > 0:
                systems = sort_results(results, sort)
                print render_table(systems, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        else:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "query failed: " + str(e)
        return


@action
def server_windows_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:server:windows settings
    section = ns.get_section('client:server:windows')
    fields = ('id','from','to','description','affected')
    fields = section.get_list('windows fields', fields)
    sort = section.get_list('windows sort', ['from','to'])
    tablefmt = section.get_str('windows table format', 'simple')
    # get the windows
    try:
        url = urljoin(server, 'objects/windows')
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
                windows = sort_results(results, sort)
                print render_table(windows, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
        else:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "query failed: " + str(e)
        return

 
    
from pesky.settings.action import Action, NOACTION
from pesky.settings.option import *

server_actions = Action("server",
                   usage="COMMAND",
                   description="Interact with server in a Mandelbrot cluster",
                   callback=NOACTION,
                   actions=[
                     Action("systems",
                       usage="[OPTIONS]",
                       description="list all systems",
                       options=[
                         Option('f', 'fields', 'systems fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'systems sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('T', 'table-format', 'systems table format', help="display result using the specified FMT", metavar="FMT")
                         ],
                       callback=server_systems_callback),
                     Action("windows",
                       usage="[OPTIONS]",
                       description="list all maintenance windows",
                       options=[
                         Option('f', 'fields', 'windows fields', help="display only the specified FIELDS", metavar="FIELDS"),
                         Option('s', 'sort', 'windows sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
                         Option('T', 'table-format', 'windows table format', help="display result using the specified FMT", metavar="FMT")
                         ],
                       callback=server_windows_callback),
                     ]
                 )
