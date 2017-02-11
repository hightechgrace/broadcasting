#!/usr/bin/env python
#
# Dashboard for streaming and recording status, formatted for
# a 20x2 character display (VFD in this case).
#
# (c) Micah Scott 2017, CC0
# https://creativecommons.org/publicdomain/zero/1.0/
#

import mi6k
from vfdwidgets import *
from dashwidgets import *

vfd = mi6k.Device().vfd
vfd.powerOn()
vfd.setBrightness(0.2)
surface = Surface(20, 2)

surface.add(Clock(gravity=(2, 1)))
surface.add(FileMonitor('/mnt/colorburst'))
surface.add(FileMonitor('/mnt/brassica'))
surface.add(FileMonitor('/mnt/cylindroid'))

while 1:
    surface.update()
    vfd.writeLines(surface.draw())
