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
from twisted.internet import reactor
from twisted.web.http_headers import Headers

from mandelbrot.client.action import action
from mandelbrot.ref import parse_proberef
from mandelbrot.http import http, as_json, from_json
from mandelbrot.editor import run_editor, strip_comments
from mandelbrot.timerange import parse_timewindow
from mandelbrot.loggers import getLogger
from mandelbrot import versionstring

logger = getLogger('mandelbrot.client.window')

initial_content = """

# Enter a description for this maintenance window.  Lines starting with
# a hash '#' are ignored.
"""

@action
def window_create_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:window:create settings
    section = ns.get_section('client:window:create')
    timerange = section.get_str('window timerange', "+ 1 hour")
    start,end = parse_timewindow(timerange)
    message = section.get_str('window message')
    # editor settings
    section = ns.get_section('editor')
    editor = section.get_path('editor')
    tmpdir = section.get_path('tmp directory')
    # get list of affected probes
    affected = ns.get_args(str, minimum=1, names=('REF',))
    # read message
    if message is None:
        message = run_editor(editor, tmpdir, initial_content)
        if message is None:
            print "error: no message was specified"
            return
        message = strip_comments(message)
        if message == "":
            print "error: no message was specified"
            return
    elif message == "-":
        message = strip_comments(sys.stdin.read())
    else:
        message = strip_comments(message)
    # create the window
    try:
        url = urljoin(server, 'objects/windows')
        logger.debug("connecting to %s", url)
        headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
        body = {'affected': affected, 'from': start.isoformat(), 'to': end.isoformat(), 'description': message}
        response = yield http.agent(timeout=3).request('POST', url, headers, as_json(body))
        logger.debug("received response %i %s", response.code, response.phrase)
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code != 202:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "command failed: " + str(e)
        return

@action
def window_modify_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:window:modify settings
    section = ns.get_section('client:window:modify')
    added = section.get_list('window add refs')
    removed = section.get_list('window remove refs')
    timerange = section.get_str('window timerange')
    message = section.get_str('window message')
    # editor settings
    section = ns.get_section('editor')
    editor = section.get_path('editor')
    tmpdir = section.get_path('tmp directory')
    # get window id
    (window,) = ns.get_args(str, minimum=1, maximum=1, names=('ID',))
    # read message
    if message is None:
        # get previous content
        try:
            url = urljoin(server, 'objects/windows')
            logger.debug("connecting to %s", url)
            response = yield http.agent(timeout=3).request('GET', url)
            logger.debug("received response %i %s", response.code, response.phrase)
            body = yield http.read_body(response)
            logger.debug("received body %s", body)
            if response.code != 200:
                raise Exception(from_json(body)['description'])
            windows = dict(map(lambda x: (x['id'], x), from_json(body)))
            if not window in windows:
                raise Exception("maintenance window %s doesn't exist" % window)
            if 'description' in windows[window]:
                description = windows[window]['description']
            else:
                description = None
        except Exception, e:
            print "query failed: " + str(e)
            return
        # run the editor using the current window description as content
        message = run_editor(editor, tmpdir, description + initial_content)
        if message is None:
            print "error: no message was specified"
            return
        message = strip_comments(message)
        if message == "":
            print "error: no message was specified"
            return
    elif message == "-":
        message = strip_comments(sys.stdin.read())
    else:
        message = strip_comments(message)
    # modify the window
    try:
        body = dict()
        if added is not None:
            body['added'] = added
        if removed is not None:
            body['removed'] = removed
        if timerange is not None:
            start,end = parse_timewindow(timerange)
            body['from'] = start.isoformat()
            body['to'] = end.isoformat()
        if message is not None:
            body['description'] = message
        url = urljoin(server, 'objects/windows/' + window)
        logger.debug("connecting to %s", url)
        headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
        response = yield http.agent(timeout=3).request('PUT', url, headers, as_json(body))
        logger.debug("received response %i %s", response.code, response.phrase)
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code != 200:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "command failed: " + str(e)
        return

@action
def window_delete_callback(ns):
    # client settings
    section = ns.get_section('client')
    server = section.get_str('supervisor url', ns.get_section('supervisor').get_str('supervisor url'))
    # client:window:create settings
    section = ns.get_section('client:window:delete')
    # get window id
    (window,) = ns.get_args(str, minimum=1, maximum=1, names=('ID',))
    # delete the window
    try:
        url = urljoin(server, 'objects/windows/' + window)
        logger.debug("connecting to %s", url)
        headers = Headers({'Content-Type': ['application/json'], 'User-Agent': ['mandelbrot-agent/' + versionstring()]})
        response = yield http.agent(timeout=3).request('DELETE', url, headers)
        logger.debug("received response %i %s", response.code, response.phrase)
        body = yield http.read_body(response)
        logger.debug("received body %s", body)
        if response.code != 200:
            print "server returned error: " + from_json(body)['description']
    except Exception, e:
        print "command failed: " + str(e)
        return


from pesky.settings.action import Action, NOACTION
from pesky.settings.option import *

window_actions = Action("window",
                   usage="COMMAND",
                   description="Interact with maintenance windows in a Mandelbrot cluster",
                   callback=NOACTION,
                   actions=[
                     Action("create",
                       usage="[OPTIONS] REF...",
                       description="create a maintenance window for the specified REFs",
                       options=[
                         Option('t', 'range', 'window timerange', help="set maintenance window to the specified TIMEWINDOW", metavar="TIMEWINDOW"),
                         Option('m', 'message', 'window message', help="use MESSAGE to describe the maintenance window", metavar="MESSAGE"),
                         ],
                       callback=window_create_callback),
                     Action("modify",
                       usage="[OPTIONS] ID",
                       description="modify an existing maintenance window",
                       options=[
                         Option('i', 'include', 'window add refs', help="Add REFs to affected list", metavar="REF..."),
                         Option('e', 'exclude', 'window remove refs', help="Remove REFs from affected list", metavar="REF..."),
                         Option('t', 'range', 'window timerange', help="set maintenance window to the specified TIMEWINDOW", metavar="TIMEWINDOW"),
                         Option('m', 'message', 'window message', help="use MESSAGE to describe the maintenance window", metavar="MESSAGE"),
                         ],
                       callback=window_modify_callback),
                     Action("delete",
                       usage="[OPTIONS] ID",
                       description="delete the specified maintenance window",
                       callback=window_delete_callback),
                     ]
                 )
