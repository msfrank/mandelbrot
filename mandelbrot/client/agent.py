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
from twisted.internet import reactor
from twisted.web.xmlrpc import Proxy
from mandelbrot.http import http, as_json, from_json
from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG

logger = getLogger('mandelbrot.client.agent')

def agent_uri_callback(ns):
    section = ns.get_section('client')
    url = 'http://localhost:9844/XMLRPC'
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    logger.debug("connecting to %s", url)
    proxy = Proxy(url)
    defer = proxy.callRemote('getUri')
    def onfailure(failure):
        print "query failed: " + failure.getErrorMessage()
        reactor.stop()
    def onresponse(uri):
        print uri
        reactor.stop()
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()

def agent_uptime_callback(ns):
    section = ns.get_section('client')
    url = 'http://localhost:9844/XMLRPC'
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    logger.debug("connecting to %s", url)
    proxy = Proxy(url)
    defer = proxy.callRemote('getUptime')
    def onfailure(failure):
        print "query failed: " + failure.getErrorMessage()
        reactor.stop()
    def onresponse(uptime):
        started = time.time() - uptime
        print "mandelbrot-agent running since " + time.ctime(started)
        reactor.stop()
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()

def agent_version_callback(ns):
    section = ns.get_section('client')
    url = 'http://localhost:9844/XMLRPC'
    if section.get_bool("debug", False):
        startLogging(StdoutHandler(), DEBUG)
    else:
        startLogging(None)
    logger.debug("connecting to %s", url)
    proxy = Proxy(url)
    defer = proxy.callRemote('getVersion')
    def onfailure(failure):
        print "query failed: " + failure.getErrorMessage()
        reactor.stop()
    def onresponse(version):
        print "mandelbrot-agent version " + version
        reactor.stop()
    defer.addCallbacks(onresponse, onfailure)
    reactor.run()


from pesky.settings.action import Action, NOACTION
from pesky.settings.option import Option, Switch

agent_actions = Action("agent",
                  usage="COMMAND",
                  description="Interact with the local agent process",
                  callback=NOACTION,
                  actions=[
                    Action("uri",
                      usage="[OPTIONS]",
                      description="display the local agent process system URI",
                      options=[],
                      callback=agent_uri_callback),
                    Action("uptime",
                      usage="[OPTIONS]",
                      description="display the local agent process uptime",
                      options=[],
                      callback=agent_uptime_callback),
                    Action("version",
                      usage="[OPTIONS]",
                      description="display the local agent process version",
                      options=[],
                      callback=agent_version_callback),
                  ])
