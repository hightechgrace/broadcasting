#!/usr/bin/env python
#
# More vfdwidgets, specifically for the streaming dashboard.
#
# (c) Micah Scott 2017, CC0
# https://creativecommons.org/publicdomain/zero/1.0/
#

from vfdwidgets import *

__all__ = []


class ProcessMonitor(Widget):
	"""Widget for monitoring a process' livelihood and CPU usage.
	   Displays different text markers when the matching process
	   is alive or dead. When alive, a spinner indicates the rate
	   of CPU usage.
	   """

    def __init__(self,
                 text       = '',
                 gravity    = (-1, -1),
                 align      = (0.5, 0.5),
                 priority   = 1,
                 background = ' ',
                 ellipses   = '',
                 visible    = True,
                 ):
        Widget.__init__(self)
        self._text = None
        self.text = text
