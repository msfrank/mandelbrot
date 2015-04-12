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

def create_command(ns):
    """

    :param ns:
    :return:
    """
    if ns.verbose == True:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format="%(asctime)s %(name)s: %(message)s")

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
    if ns.verbose == True:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format="%(asctime)s %(name)s: %(message)s")

    endpoint_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    check_executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)
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
    if ns.verbose == True:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format="%(asctime)s %(name)s: %(message)s")
    return 0
