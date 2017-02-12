#!/usr/bin/env python
#
# Dashboard for streaming and recording status, formatted for
# a 20x2 character display (VFD in this case).
#
# (c) Micah Scott 2017, CC0
# https://creativecommons.org/publicdomain/zero/1.0/
#

import mi6k
import textwrap
from dashwidgets import *

widgets = [
    FileSizePoller('cb', '/mnt/colorburst'),
    FileSizePoller('aud', '/mnt/cylindroid/vidblog Project'),
    FileSizePoller('fsh', '/mnt/cylindroid/Game Capture HD Library'),
    FileSizePoller('br', '/mnt/brassica'),
    FileSizePoller('cyo', '/mnt/cylindroid/obs'),
    ProcessPoller('#test', '/home/micah/announce/test.js'),
    ProcessPoller('#senrio', '/home/micah/announce/senrio.js'),
    ProcessPoller('#scanlime', '/home/micah/announce/scanlime.js'),
    ProcessPoller('+ffm', '/usr/local/bin/ffmpeg'),
    ClockWidget()
]

vfd = mi6k.Device().vfd
vfd.powerOn()
vfd.setBrightness(0.2)

while 1:
    texts = ' '.join(filter(None, map(str, widgets)))
    screen = '\n'.join(textwrap.wrap(texts, mi6k.CenturyVFD.width)[:mi6k.CenturyVFD.lines])
    vfd.writeScreen(screen)
