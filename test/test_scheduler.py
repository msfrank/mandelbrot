import bootstrap

import unittest
import asyncio

import mandelbrot.agent.scheduler

class TestScheduler(unittest.TestCase):

    def f1():
        return "f1"
    def f2():
        return "f2"
    def f3():
        return "f3"

    def test_schedule_tasks_in_order(self):
        "A Scheduler should schedule tasks in order"
        event_loop = asyncio.new_event_loop()
        scheduler = mandelbrot.agent.scheduler.Scheduler(event_loop)
        scheduler.schedule_task(self.f1, 1.0, 0.2, 0.0)
        scheduler.schedule_task(self.f2, 1.0, 0.4, 0.0)
        scheduler.schedule_task(self.f3, 1.0, 0.6, 0.0)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f1)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f2)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f3)

    def test_schedule_tasks_out_of_order(self):
        "A Scheduler should schedule tasks in order when submitted out of order"
        event_loop = asyncio.new_event_loop()
        scheduler = mandelbrot.agent.scheduler.Scheduler(event_loop)
        scheduler.schedule_task(self.f1, 3.0, 0.0, 0.0)
        scheduler.schedule_task(self.f2, 3.0, 1.2, 0.0)
        scheduler.schedule_task(self.f3, 3.0, 0.6, 0.0)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f1)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f3)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f2)

    def test_unschedule_task(self):
        "A Scheduler should remove an unscheduled task"
        event_loop = asyncio.new_event_loop()
        scheduler = mandelbrot.agent.scheduler.Scheduler(event_loop)
        scheduler.schedule_task(self.f1, 3.0, 0.0, 0.0)
        scheduler.schedule_task(self.f2, 3.0, 0.5, 0.0)
        scheduler.schedule_task(self.f3, 3.0, 1.0, 0.0)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f1)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f2)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f3)
        scheduler.unschedule_task(self.f2)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f1)
        f = event_loop.run_until_complete(asyncio.wait_for(scheduler.next_task(), 5.0, loop=event_loop))
        self.assertEquals(f, self.f3)


