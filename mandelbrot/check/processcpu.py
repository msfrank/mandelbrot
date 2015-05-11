import time
import psutil
import cifparser

from mandelbrot.check.process import ProcessCheck
from mandelbrot.model.evaluation import *

class ProcessCPU(ProcessCheck):
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
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarCheck"

    def get_behavior(self):
        return {}

    def init(self):
        super().init()
        self.systemfailed = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "system failed threshold")
        self.systemdegraded = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "system degraded threshold")
        self.userfailed = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "user failed threshold")
        self.userdegraded = self.ns.get_percentage_or_default(cifparser.ROOT_PATH, "user degraded threshold")
        context = {}
        process = self.get_process(context)
        if process is None:
            return context
        user_time, system_time = process.cpu_times()
        context['created'] = process.create_time()
        context['pid'] = process.pid
        context['system_time'] = system_time
        context['user_time'] = user_time
        context['timestamp'] = time.time()
        return context

    def execute(self, evaluation, context):
        # find the current process incarnation
        process = self.get_process(context)

        # no procss running, complete with UNKNOWN health
        if process is None:
            evaluation.set_health(UNKNOWN)
            context.clear()
        
        # snapshot the current process
        created = process.create_time()
        pid = process.pid
        user_time, system_time = process.cpu_times()
        timestamp = time.time()

        # calculate the system and user time
        if len(context) > 0:
            duration = timestamp - context['timestamp']
            system = (system_time - context['system_time']) / duration
            user = (user_time - context['user_time']) / duration
        else:
            duration = timestamp - created
            system = system_time / duration
            user = user_time / duration

        # update the context
        context['created'] = created
        context['pid'] = pid
        context['system_time'] = system_time
        context['user_time'] = user_time
        context['timestamp'] = timestamp

        # perform the evaluation
        evaluation.set_summary("process %i CPU utilization is %.1f%% user, %.1f%% system" % (
            pid, user * 100.0, system * 100.0))
        if self.systemfailed is not None and system > self.systemfailed:
            evaluation.set_health(FAILED)
        elif self.userfailed is not None and user > self.userfailed:
            evaluation.set_health(FAILED)
        elif self.systemdegraded is not None and system > self.systemdegraded:
            evaluation.set_health(DEGRADED)
        elif self.userdegraded is not None and user > self.userdegraded:
            evaluation.set_health(DEGRADED)
        else:
            evaluation.set_health(HEALTHY)
