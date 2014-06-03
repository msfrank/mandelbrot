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
from urllib import urlencode
from urlparse import urljoin
from twisted.web.xmlrpc import Proxy
from twisted.web.http_headers import Headers

from mandelbrot.client.action import action
from mandelbrot.ref import parse_proberef
from mandelbrot.http import http, as_json, from_json
from mandelbrot.table import sort_results, render_table
from mandelbrot.loggers import getLogger
from mandelbrot import versionstring

logger = getLogger('mandelbrot.client.local')

from mandelbrot.table import millis2ctime, bool2checkbox, proberef2path
renderers = {
    'probeRef': proberef2path,
    'lastChange': millis2ctime,
    'lastUpdate': millis2ctime,
    'timestamp':  millis2ctime,
    'acknowledged': bool2checkbox,
    'squelched':  bool2checkbox,
}

@action
def status_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:status settings
    section = ns.get_section('client:status')
    fields = ('probeRef','lifecycle','health','acknowledged','summary','lastChange','lastUpdate','squelched')
    fields = section.get_list('status fields', fields)
    sort = section.get_list('status sort', ['probeRef'])
    tablefmt = section.get_str('status table format', 'simple')
    paths = urlencode(map(lambda arg: ('path', arg), ns.get_args()))
    # get the system uri
    agent_url = 'http://localhost:9844/XMLRPC'
    proxy = Proxy(agent_url)
    try:
        system = yield proxy.callRemote('getUri')
    except Exception, e:
        print "failed to discover agent system uri: " + str(e)
        return
    # get the status
    try:
        url = urljoin(server, 'objects/systems/' + str(system) + '/properties/status?' + paths)
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
        

@action
def acknowledge_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:acknowledge settings
    section = ns.get_section('client:acknowledge')
    paths = urlencode(map(lambda arg: ('path', arg), ns.get_args()))
    # get the system uri
    agent_url = 'http://localhost:9844/XMLRPC'
    proxy = Proxy(agent_url)
    try:
        system = yield proxy.callRemote('getUri')
    except Exception, e:
        print "failed to discover agent system uri: " + str(e)
        return
    # get the status
    try:
        url = urljoin(server, 'objects/systems/' + str(system) + '/properties/status?' + paths)
        logger.debug("connecting to %s", url)
        response = yield http.agent(timeout=3).request('GET', url)
        logger.debug("received response %i %s", response.code, response.phrase)
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code != 200:
            print "server returned error: " + from_json(body)['description']
        correlations = dict(map(lambda x: (x['probeRef'], x['correlation']),
            filter(lambda x: 'correlation' in x and not 'acknowledgement' in x, from_json(body).values()
            )))
    except Exception, e:
        print "query failed: " + str(e)
        return
    # acknowledge probes
    try:
        url = urljoin(server, 'objects/systems/' + str(system) + '/actions/acknowledge')
        logger.debug("connecting to %s", url)
        headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
        body = {'uri': str(system), 'correlations': correlations}
        response = yield http.agent(timeout=3).request('POST', url, headers, as_json(body))
        logger.debug("received response %i %s", response.code, response.phrase)
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code != 200:
            print "server returned error: " + from_json(body)['description']
        acknowledgements = dict(map(lambda (ref,ack): (parse_proberef(ref), ack), from_json(body).items()))
    except Exception, e:
        print "command failed: " + str(e)


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
        Option('m', 'message', 'message', help="append MESSAGE to the acknowledgement", metavar="MESSAGE"),
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
