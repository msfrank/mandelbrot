import os
import sys
import concurrent.futures
import pathlib
import logging
import daemon
import lockfile
import signal

from mandelbrot.instance import create_instance
from mandelbrot.agent.supervisor import Supervisor

logging_format="%(asctime)s %(message)s"
debug_format="%(asctime)s %(levelname)s %(name)s: %(message)s"

def create_command(ns):
    """

    :param ns:
    :return:
    """
    if ns.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format=debug_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)

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
            filename=ns.log_file, format=logging_format)
    else:
        logging.basicConfig(level=getattr(logging, ns.log_level),
            filename=os.path.join(ns.path, 'agent.log'), format=logging_format)

    pool_workers = ns.pool_workers
    endpoint_executor = concurrent.futures.ThreadPoolExecutor(max_workers = pool_workers * 2)
    check_executor = concurrent.futures.ProcessPoolExecutor(max_workers = pool_workers)
    supervisor = Supervisor(ns.path, endpoint_executor, check_executor)

    pidfile = os.path.join(ns.path, 'agent.pid')

    daemon_context = daemon.DaemonContext(
        working_directory = ns.path,
        pidfile = lockfile.LockFile(pidfile),
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

    with daemon_context:
        with open(pidfile, 'w') as f:
            f.write(str(os.getpid()) + '\n')
        supervisor.run_forever()
        os.remove(pidfile)
    return 0

def stop_command(ns):
    """

    :param ns:
    :return:
    """
    return 0
