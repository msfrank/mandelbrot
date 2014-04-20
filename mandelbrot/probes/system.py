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

import os, psutil
from mandelbrot.probes import Probe
from mandelbrot.evaluation import Evaluation, EvaluationState


class SystemLoad(Probe):
    """
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemLoad"

    def probe(self):
        load1, load5, load15 = os.getloadavg()
        ncores = psutil.cpu_count()
        summary = "load average is %.1f %.1f %.1f, detected %i cores" % (load1,load5,load15,ncores)
        return Evaluation(EvaluationState.STATE_HEALTHY, summary)

class SystemCPU(Probe):
    """
    """
    def __init__(self):
        Probe.__init__(self)
        # throw away the first value
        psutil.cpu_times_percent()

    def get_type(self):
        return "io.mandelbrot.probe.SystemCPU"

    def probe(self):
        times = psutil.cpu_times_percent()
        user = times.user
        nice = times.nice
        system = times.system
        idle = times.idle
        summary = "CPU utilization is %.1f%% user, %.1f%% system, %.1f%% idle, %.1f%% nice" % (user,system,idle,nice)
        return Evaluation(EvaluationState.STATE_HEALTHY, summary)

class SystemMemory(Probe):
    """
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemMemory"

    def probe(self):
        memory = psutil.virtual_memory()
        memused = memory.percent
        memtotal = memory.total
        swap = psutil.swap_memory()
        swapused = swap.percent
        swaptotal = swap.total
        summary = "%.1f%% used of %i bytes of physical memory; %.1f%% used of %i bytes of swap" % (memused,memtotal,swapused,swaptotal)
        return Evaluation(EvaluationState.STATE_HEALTHY, summary)
