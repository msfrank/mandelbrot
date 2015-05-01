import re
import psutil
import cifparser

from mandelbrot.check import Check

class ProcessCheck(Check):
    """
    Check process CPU utilization.

    Parameters:
    system failed threshold   = CPU: percentage
    system degraded threshold = CPU: percentage
    user failed threshold     = CPU: percentage
    user degraded threshold   = CPU: percentage
    process pid file          = PIDFILE: str
    process name matches      = NAME: str
    process exe matches       = EXE: str
    process cmdline matches   = CMDLINE: str
    process owner matches     = OWNER: str
    """
    def _matches_process(self, p):
        if self.namematches is not None and not re.match(self.namematches, p.name()):
            return False
        if self.exematches is not None and not re.match(self.exematches, p.exe()):
            return False
        if self.cmdlinematches is not None and not re.match(self.cmdlinematches, p.cmdline()):
            return False
        if self.ownermatches is not None and not re.match(self.ownermatches, p.username()):
            return False
        return True

    def get_process(self, context):
        pid = context.get('pid')
        created = context.get('created')
        # check if the pid from context is the same incarnation
        if pid is not None and created is not None:
            p = psutil.Process(pid)
            if p.create_time() == created:
                return p
        # if pidfile is specified, then read the pid
        if self.pidfile is not None:
            with open(self.pidfile, 'r') as f:
                p = psutil.Process(int(f.read().strip()))
            if self._matches_process(p):
                return p
        # otherwise iterate through all processes to find a single match
        process = None
        for p in psutil.process_iter():
            if self._matches_process(p):
                if process is not None:
                    raise Exception("process is not unique")
                process = p
        return process

    def init(self):
        self.pidfile = self.ns.get_str_or_default(cifparser.ROOT_PATH, "process pid file")
        self.namematches = self.ns.get_str_or_default(cifparser.ROOT_PATH, "process matches name")
        self.exematches = self.ns.get_str_or_default(cifparser.ROOT_PATH, "process matches exe")
        self.cmdlinematches = self.ns.get_str_or_default(cifparser.ROOT_PATH, "process matches cmdline")
        self.ownermatches = self.ns.get_str_or_default(cifparser.ROOT_PATH, "process matches owner")
        # there must be at least one parameter specified to
        # uniquely match a process
        if (self.pidfile is None and
            self.namematches is None and
            self.exematches is None and
            self.cmdlinematches is None and
            self.ownermatches is None):
            raise Exception("either 'process pid file' or 'process matches' parameter is required")
        return None
