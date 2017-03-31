"""Timers"""
import asyncio
import logging
import time

from .dispatcher import Dispatcher

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
    def __init__(self, start_time=0, period=1.25):
        self._time = Time(start_time)
        self._ticker = asyncio.Task(self._update(period))
        self._tasks = []

    async def _update(self, period):
        while True:
            await asyncio.sleep(period)
            log.info('Time {}'.format(self._time()))
            keep = []
            for task in self._tasks:
                if await self._dispatch(task):
                    keep.append(task)
            self._tasks = keep

    async def _dispatch(self, atask):
        if atask.deadline <= self._time():
            await Dispatcher.dispatch(atask)
            self._tasks = [x for x in self._tasks if x is not atask]
            return False

        return True

    def schedule(self, task):
        task.deadline = self._time() + task.after
        self._tasks.append(task)

    def stop(self):
        self._ticker.cancel()
