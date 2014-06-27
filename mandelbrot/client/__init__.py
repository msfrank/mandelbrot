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

import os, sys, traceback
from pesky.settings.action import ActionMap, Action
from pesky.settings.option import Option, LongOption, Switch
from pesky.settings.errors import ConfigureError

from mandelbrot.client.agent import agent_actions
from mandelbrot.client.local import local_actions
from mandelbrot.client.search import search_actions
from mandelbrot.client.server import server_actions
from mandelbrot.client.system import system_actions
from mandelbrot.client.window import window_actions
from mandelbrot.loggers import getLogger
from mandelbrot.defaults import defaults
from mandelbrot import versionstring

logger = getLogger('mandelbrot.client')

def main():
    try:
        actions = ActionMap(
          usage="[OPTIONS...] COMMAND",
          version=versionstring(),
          description="Mandelbrot client commands",
          appname="mandelbrot",
          confbase=os.path.abspath(defaults["SYSCONF_DIR"]),
          section="client",
          options=[
            Option("H", "host", override="supervisor url", help="Connect to mandelbrot server HOST", metavar="HOST"),
            Option("u", "username", override="username", help="Authenticate with username USER", metavar="USER"),
            Option("p", "password", override="password", help="Authenticate with password PASS", metavar="PASS"),
            Switch("P", "prompt-password", override="prompt password", help="Prompt for a password"),
            LongOption("log-config", override="log config file", help="use logging configuration file FILE", metavar="FILE"),
            Switch("d", "debug", override="debug", help="Print debugging information")],
          actions = local_actions + [ agent_actions, system_actions, server_actions, search_actions, window_actions ]
        )
        return actions.parse()
    except ConfigureError, e:
        print >> sys.stderr, "%s: %s" % (actions.settings.appname, e)
    except Exception, e:
        print >> sys.stderr, "\nUnhandled Exception:\n%s\n---\n%s" % (e,traceback.format_exc())
    sys.exit(1)
