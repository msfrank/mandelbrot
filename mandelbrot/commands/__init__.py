daemon_format="%(asctime)s %(message)s"
debug_format="%(asctime)s %(levelname)s %(name)s: %(message)s"
utility_format="%(message)s"

import contextlib

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


