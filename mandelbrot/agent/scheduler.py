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

import asyncio
import random
import logging

log = logging.getLogger("mandelbrot.agent.scheduler")

class Scheduler(object):
    """
    """
    def __init__(self, event_loop):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        """
        self.event_loop = event_loop
        self.task_list = {}
        self.queue = asyncio.Queue(loop=event_loop)

    def schedule_task(self, f, delay, offset, jitter):
        """
        :param f:
        :type f: callable
        :param delay:
        :type delay: float
        :param offset:
        :type offset: float
        :param jitter:
        :type jitter: float
        """
        if f in self.task_list:
            raise KeyError("{} is already scheduled".format(f))
        task = ScheduledTask(self.event_loop, self.queue, f, delay, offset, jitter)
        self.task_list[task.f] = task

    def unschedule_task(self, f):
        """
        :param f:
        :type f: callable
        """
        try:
            task = self.task_list[f]
            task.cancel()
            del self.task_list[f]
        except:
            raise KeyError("{} is not scheduled".format(f))

    def next_task(self):
        """
        :returns: The next scheduled task function.
        :rtype: callable
        """
        return self.queue.get()

    def unschedule_all(self):
        """
        """
        for task in self.task_list.values():
            task.cancel()
        self.task_list = {}

class ScheduledTask(object):
    """
    """
    def __init__(self, event_loop, queue, f, delay, offset, jitter):
        """
        :param event_loop:
        :type event_loop: asyncio.AbstractEventLoop
        :param queue:
        :type queue: asyncio.Queue
        :param f:
        :type f: callable
        :param delay:
        :type delay: float
        :param offset:
        :type offset: float
        :param jitter:
        :type jitter: float
        """
        self.event_loop = event_loop
        self.queue = queue
        self.f = f
        self.delay = delay
        self.offset = offset
        self.jitter = random.random() * jitter
        self.next_scheduled_time = self.current_time() + self.offset + self.jitter
        self.handle = self.event_loop.call_at(self.next_scheduled_time, self._enqueue)
        log.debug("scheduling %s at %s (%.3fs offset %.3fs jitter)", self.f, self.next_scheduled_time, self.offset, self.jitter)

    def current_time(self):
        """
        :rtype: float
        """
        return self.event_loop.time()

    def _enqueue(self):
        try:
            self.queue.put_nowait(self.f)
        except asyncio.QueueFull:
            log.error("failed to enqueue scheduled task, queue is full")
        self.next_scheduled_time = self.current_time() + self.delay
        self.handle = self.event_loop.call_at(self.next_scheduled_time, self._enqueue)
        log.debug("scheduling %s at %s (%.3fs delay)", self.f, self.next_scheduled_time, self.delay)

    def is_running(self):
        return self.handle is not None

    def cancel(self):
        if self.is_running():
            log.debug("cancelled %s", self.f)
            self.handle.cancel()
            self.handle = None
