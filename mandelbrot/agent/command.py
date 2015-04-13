import os
import sys
import concurrent.futures
import pathlib
import contextlib
import logging
import psutil
import daemon
import lockfile
import signal

from mandelbrot.instance import create_instance
from mandelbrot.agent.supervisor import Supervisor

daemon_format="%(asctime)s %(message)s"
debug_format="%(asctime)s %(levelname)s %(name)s: %(message)s"
utility_format="%(message)s"

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

def create_command(ns):
    """

    :param ns:
    :return:
    """
    if ns.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format=utility_format)
    else:
        logging.basicConfig(level=logging.INFO, format=utility_format)
    log = logging.getLogger('mandelbrot')

    agent_id = ns.agent_id
    endpoint_url = ns.endpoint_url
    instance = create_instance(pathlib.Path(ns.path))

    with instance.lock():
        instance.set_agent_id(agent_id)
        instance.set_endpoint_url(endpoint_url)
    return 0

def start_command(ns):
    """

    :param ns:
    :return:
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

    pool_workers = ns.pool_workers
    endpoint_executor = concurrent.futures.ThreadPoolExecutor(max_workers = pool_workers * 2)
    check_executor = concurrent.futures.ProcessPoolExecutor(max_workers = pool_workers)
    supervisor = Supervisor(ns.path, endpoint_executor, check_executor)

    pidfile = os.path.join(ns.path, 'agent.pid')

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

def stop_command(ns):
    """

    :param ns:
    :return:
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
        import errno
        if e.errno == errno.ENOENT:
            print("agent {0} is not running".format(ns.path))
            return 1
        raise

def status_command(ns):
    """
    :param ns:
    :return:
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
        print("agent {0} running with pid {1}".format(ns.path, pid))
        return 0
    except OSError as e:
        import errno
        if e.errno == errno.ENOENT:
            print("agent {0} is not running".format(ns.path))
            return 1
        raise
