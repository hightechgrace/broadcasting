#!/usr/bin/env python
#
# More vfdwidgets, specifically for the streaming dashboard.
#
# (c) Micah Scott 2017, CC0
# https://creativecommons.org/publicdomain/zero/1.0/
#

import psutil
import os
import stat
import threading
import time

__all__ = [ 'FileSizePoller', 'ProcessPoller', 'ClockWidget' ]


def recursive_file_size(path):
    try:
        s = os.lstat(path)
    except OSError:
        return
    if stat.S_ISDIR(s.st_mode):
        try:
            dirs = os.listdir(path)
        except OSError:
            return
        total = None
        for name in dirs:
            total = (total or 0) + (recursive_file_size(os.path.join(path, name)) or 0)
        return total
    if stat.S_ISREG(s.st_mode):
        return s.st_size


class ResourcePoller(threading.Thread):
    def __init__(self, interval=1.0):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.dt_filter = 0

    def run(self):
        saved_time = time.time()
        self.timestamp = saved_time
        self.poll(None)
        while True:
            self.timestamp += self.interval
            this_time = time.time()
            dt = this_time - saved_time
            self.poll(dt)
            saved_time = this_time
            delay = self.timestamp - this_time

            if abs(delay) > self.interval * 10:
                # Give up, reset intended timestamp
                self.timestamp = this_time
            elif delay > 0.010:
                # Enough accumulated delay to sleep
                time.sleep(delay)

    def poll(self, dt):
        raise NotImplementedError


class ClockWidget:
    def __init__(self, format='%l:%M:%S %p'):
        self.format = format

    def __str__(self):
        return time.strftime(self.format).strip()


class FileSizePoller(ResourcePoller):
    def __init__(self, label, path, interval=1.25):
        ResourcePoller.__init__(self, interval)
        self.label = label
        self.path = path
        self.size = None
        self.free = None
        self.rate = None
        self.start()

    def poll(self, dt=None):
        last_size = self.size
        try:
            self.size = recursive_file_size(self.path)
            self.free = psutil.disk_usage(self.path).free
        except OSError:
            return
        if dt and last_size:
            self.rate = (self.size - last_size) / dt
        else:
            self.rate = None

    def __str__(self):
        if self.rate is None:
            return '!%s' % self.label
        if self.rate <= 0:
            return ''
        gbfree = self.free / (1.0*1024*1024*1024)
        summary = '%s:%.1fM' % (self.label, self.rate / (1.0*1024*1024))
        if gbfree < 1000:
            summary += '[%.0f]' % gbfree
        return summary


class ProcessPoller(ResourcePoller):
    def __init__(self, label, pattern, interval=2.5):
        ResourcePoller.__init__(self, interval)
        self.label = label
        self.pattern = pattern
        self.process = None
        self.start()

    def poll(self, dt=None):
        for p in psutil.process_iter():
            if self.pattern in p.cmdline():
                self.process = p
                return
        self.process = None

    def __str__(self):
        if self.process:
            return self.label
        else:
            return ''
