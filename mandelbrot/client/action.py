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

from mandelbrot.loggers import getLogger, startLogging, StdoutHandler, DEBUG

logger = getLogger('mandelbrot.client.action')

def action(fn):
    """
    Decorator which wraps an action callback conforming to the twisted
    inlineCallbacks interface.  This lets us write synchronous-looking code
    that uses asynchronous methods from twisted.
    """
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks
    from twisted.python.failure import Failure
    inlinefn = inlineCallbacks(fn)
    def on_return(ret):
        if isinstance(ret, Failure):
            logger.debug("action failed: %s", failure.getErrorMessage())
        reactor.stop()
    def trampoline(ns):
        section = ns.get_section('client')
        debug = section.get_bool("debug", False)
        if debug:
            startLogging(StdoutHandler(), DEBUG)
        else:
            startLogging(None)
        defer = inlinefn(ns)
        defer.addBoth(on_return)
        reactor.run()
    return trampoline
