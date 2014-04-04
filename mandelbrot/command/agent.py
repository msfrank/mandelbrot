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

import sys, traceback
from pesky.settings import Settings, ConfigureError
from mandelbrot import versionstring
from mandelbrot.agent import Agent

def main():
    settings = Settings(
        usage="[OPTIONS...]",
        version=versionstring(),
        description="Mandelbrot agent",
        appname="mandelbrot-agent",
        confbase="/etc/mandelbrot",
        section="agent")
    try:
        settings.add_switch("f", "foreground",
            override="stay in foreground", help="Do not fork into the background"
            )
        settings.add_longoption("log-config",
            override="log config file", help="use logging configuration file FILE", metavar="FILE"
            )
        settings.add_switch("d", "debug",
            override="debug", help="Emit lots of debugging information"
            )
        # load configuration
        ns = settings.parse()
        # create the Agent and run it
        agent = Agent()
        agent.configure(ns)
        return agent.run()
    except ConfigureError, e:
        print >> sys.stderr, "%s: %s" % (settings.appname, e)
    except Exception, e:
        print >> sys.stderr, "\nUnhandled Exception:\n%s\n---\n%s" % (e,traceback.format_exc())
    sys.exit(1)
