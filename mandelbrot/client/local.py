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

import time
from urlparse import urljoin
from twisted.internet import reactor
from twisted.web.xmlrpc import Proxy
from mandelbrot.http import http, as_json, from_json
from mandelbrot.table import sort_results, render_table
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG

logger = getLogger('mandelbrot.client.local')

from mandelbrot.table import millis2ctime, bool2checkbox, proberef2path
renderers = {
    'probeRef': proberef2path,
    'lastChange': millis2ctime,
    'lastUpdate': millis2ctime,
    'timestamp':  millis2ctime,
    'squelched':  bool2checkbox,
}

def status_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('host')
    debug = section.get_bool("debug", False)
    # client:status settings
    section = ns.get_section('client:status')
    fields = ('probeRef','lifecycle','health','summary','timestamp','lastChange','lastUpdate','squelched')
    fields = section.get_list('status fields', fields)
    sort = section.get_list('status sort', ['probeRef'])
    tablefmt = section.get_str('status table format', 'simple')
    refs = ns.get_args()
    if debug:
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    # 
    agent_url = 'http://localhost:9844/XMLRPC'
    proxy = Proxy(agent_url)
    defer = proxy.callRemote('getUri')
    def on_uri(system):
        url = urljoin(server, 'objects/systems/' + str(system) + '/properties/status')
        logger.debug("connecting to %s", url)
        defer = http.agent(timeout=3).request('GET', url)
        def on_body(body, code):
            logger.debug("received body %s", body)
            if code == 200:
                status = sort_results(from_json(body), sort)
                print render_table(status, expand=False, columns=fields, renderers=renderers, tablefmt=tablefmt)
            else:
                print "error: " + from_json(body)['description']
            reactor.stop()
        def on_failure(failure):
            logger.debug("query failed: %s", failure.getErrorMessage())
            reactor.stop()
        def on_response(response):
            logger.debug("received response %i %s", response.code, response.phrase)
            http.read_body(response).addCallbacks(on_body, on_failure, callbackArgs=(response.code,))
        defer.addCallbacks(on_response, on_failure)
    def on_failure(failure):
        print "failed to discover agent system uri: " + failure.getErrorMessage()
        reactor.stop()
    defer.addCallbacks(on_uri, on_failure)
    reactor.run()

def acknowledge_callback(ns):
    pass

def unacknowledge_callback(ns):
    pass

def disable_callback(ns):
    pass

def enable_callback(ns):
    pass


from pesky.settings.action import Action, NOACTION
from pesky.settings.option import Option, Switch

local_actions = [
    Action("status",
      usage="[OPTIONS] [PATH...]",
      description="get the current status of local PATH",
      options=[
        Option('f', 'fields', 'status fields', help="display only the specified FIELDS", metavar="FIELDS"),
        Option('s', 'sort', 'status sort', help="sort results using the specified FIELDS", metavar="FIELDS"),
        Option('T', 'table-format', 'status table format', help="display result using the specified FMT", metavar="FMT")
        ],
      callback=status_callback),
    Action("acknowledge",
      usage="[OPTIONS] [PATH...]",
      description="acknowledge unhealthy local PATH",
      options=[
        Option('m', 'message', 'message', help="Use the given MESSAGE as the acknowledgement message", metavar="MESSAGE"),
        ],
      callback=acknowledge_callback),
    Action("unacknowledge",
      usage="[OPTIONS] [PATH...]",
      description="remove acknowledgement of unhealthy local PATH",
      options=[
        Option('m', 'message', 'message', help="Use the given MESSAGE as the acknowledgement message", metavar="MESSAGE"),
        ],
      callback=unacknowledge_callback),
    Action("disable",
      usage="[OPTIONS] [PATH...]",
      description="disable notifications for local PATH",
      options=[],
      callback=disable_callback),
    Action("enable",
      usage="[OPTIONS] [PATH...]",
      description="enable notifications for local PATH",
      options=[],
      callback=enable_callback),
    ]
