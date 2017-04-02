"""Timers"""
import asyncio
import collections
import logging
import time

log = logging.getLogger(__name__)


class Time(object):
    __slots__ = ['_time', '_mono']

    def __init__(self, start):
        super().__init__()
        self._mono = time.monotonic()
        self._time = start

    def __call__(self):
        mono_time = time.monotonic()
        delta = mono_time - self._mono
        self._mono = mono_time
        self._time += delta
        return self._time


class Timers(object):
    def __init__(self, start_time=0):
        self._time = Time(start_time)
        self._ticker = None
        self._tasks = collections.deque()

    async def _wait_for(self, period):
        try:
            await asyncio.sleep(period)
            ctime = self._time()

            execute = []
            rest = []
            for deadline, task in self._tasks:
                if deadline <= ctime:
                    execute.append(task)
                else:
                    rest.append((deadline, task))

            self._tasks = rest
            for task in execute:
                task.action(task.target, *task.args)

            if self._tasks:
                self._ticker = asyncio.get_event_loop().create_task(
                    self._wait_for(self._tasks[0][0] - self._time())
                )

        except asyncio.CancelledError:
            pass

    def schedule(self, task):
        ctime = self._time()
        deadline = ctime + task.after
        if deadline <= ctime:
            task.action(task.target, *task.args)
        else:
            self._tasks.append((deadline, task))
            self._tasks = sorted(self._tasks, key=lambda x: x[0])
            if deadline <= self._tasks[0][0]:
                if self._ticker:
                    self._ticker.cancel()
                self._ticker = asyncio.get_event_loop().create_task(
                    self._wait_for(deadline - self._time())
                )

    def stop(self):
        if self._ticker:
            self._ticker.cancel()
