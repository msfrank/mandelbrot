import os
import sys
import concurrent.futures
import logging
import contextlib
import daemon
import lockfile
import signal

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

def start_main(ns):
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
