#!/usr/bin/env python
#
# More vfdwidgets, specifically for the streaming dashboard.
#
# (c) Micah Scott 2017, CC0
# https://creativecommons.org/publicdomain/zero/1.0/
#

from vfdwidgets import Text
import psutil
import humanfriendly

import os
import stat
import threading
import time

__all__ = [ 'FileMonitor' ]


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


def format_size(number):
    if number is None:
        return '-'
    return humanfriendly.format_size(number)


def format_bitrate(bytes_per_second):
    if bytes_per_second is None:
        return '-'
    return "%.0f Kbps" % ((bytes_per_second * 8) / 1000.0)


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


class FileSizePoller(ResourcePoller):
    def __init__(self, path, interval=1.0):
        ResourcePoller.__init__(self, interval)
        self.path = path
        self.size = None
        self.free = None
        self.rate = None

    def poll(self, dt=None):
        last_size = self.size
        try:
            self.size = recursive_file_size(self.path)
            self.free = psutil.disk_usage(self.path).free
        except OSError:
            pass
        if dt and last_size:
            self.rate = (self.size - last_size) / dt
        else:
            self.rate = None

        print format_size(self.size), format_size(self.free), format_bitrate(self.rate)


class FileMonitor(Text):
    def __init__(self, path,
                 interval   = 2.0,
                 gravity    = (-1, -1),
                 align      = (0.5, 0.5),
                 priority   = 1,
                 ):
        Text.__init__(self, '-'*6, gravity=gravity, align=align, priority=priority)
        self.poller = FileSizePoller(path, interval)
        self.poller.start()

    def update(self, dt):
        self.text = str(dt)

