# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
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

import os
import sys
import logging
import contextlib
import daemon
import lockfile
import signal
import cifparser

from mandelbrot.log import daemon_format, debug_format
from mandelbrot.agent.supervisor import Supervisor

@contextlib.contextmanager
def with_timeout(timeout, lock):
    """
    wraps the specified lockfile and calls acquire with a timeout.

    :param timeout:
    :type timeout: float
    :param lock:
    :type lock: lockfile.LockFile
    :return:
    """
    lock.acquire(timeout)
    yield lock
    lock.release()

def run_command(ns):
    """
    """
    if ns.debug:
        logging.basicConfig(level=logging.DEBUG, format=debug_format)
    elif ns.log_file is not None:
        logging.basicConfig(level=getattr(logging, ns.log_level),
            filename=ns.log_file, format=daemon_format)
    else:
        logging.basicConfig(level=getattr(logging, ns.log_level),
            filename=os.path.join(ns.path, 'agent.log'), format=daemon_format)
    log = logging.getLogger('mandelbrot')

    pidfile = os.path.join(ns.path, 'agent.pid')

    values = cifparser.ValueTree()
    values.put_container('mandelbrot.agent')
    values.put_field('mandelbrot.agent', 'pool workers', str(ns.pool_workers))
    settings = cifparser.Namespace(values)

    supervisor = Supervisor(ns.path, settings)
    daemon_context = daemon.DaemonContext(
        working_directory = ns.path,
        pidfile = with_timeout(-1, lockfile.LockFile(pidfile)),
        detach_process = not ns.foreground,
        stdin = sys.stdin,
        stdout = sys.stdout,
        stderr = sys.stderr,
        files_preserve = [fd for fd in range(64)],
        signal_map = {
            signal.SIGTTIN : None,
            signal.SIGTTOU : None,
            signal.SIGTSTP : None,
            signal.SIGTERM : None
        }
    )

    try:
        with daemon_context:
            with open(pidfile, 'w') as f:
                f.write(str(os.getpid()) + '\n')
            supervisor.run_forever()
            os.remove(pidfile)
        return 0
    except lockfile.AlreadyLocked as e:
        log.error(str(e))
        return 1
