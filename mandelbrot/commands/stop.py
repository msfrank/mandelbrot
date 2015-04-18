import os
import sys
import pathlib
import logging
import psutil
import signal
import errno

from mandelbrot.instance import create_instance
from mandelbort.commands import utility_format

def stop_main(ns):
    """
    """
    if ns.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format=utility_format)
    else:
        logging.basicConfig(level=logging.INFO, format=utility_format)
    log = logging.getLogger('mandelbrot')

    try:
        instance_path = pathlib.Path(ns.path)
        if not instance_path.is_dir():
            print("no agent exists at {0}".format(ns.path))
            return 2
        pidfile = os.path.join(ns.path, 'agent.pid')
        with open(pidfile, 'r') as f:
            pid = int(f.read())
        if not psutil.pid_exists(pid):
            print("agent {0} not running, but a stale pidfile exists at {1}".format(ns.path, pidfile))
            return 1
        os.kill(pid, signal.SIGTERM)
        log.debug("sent SIGTERM to pid %s", pid)
        return 0
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("agent {0} is not running".format(ns.path))
            return 1
        raise
