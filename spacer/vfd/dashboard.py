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

brightnessLevels = (0.0, 1.0)

proc = ProcessPoller()

dash = [
    FileSizePoller('cb', '/mnt/colorburst'),
    FileSizePoller('aud', '/mnt/cylindroid/vidblog Project'),
    FileSizePoller('fsh', '/mnt/cylindroid/Game Capture HD Library'),
    FileSizePoller('br', '/mnt/brassica'),
    FileSizePoller('cyo', '/mnt/cylindroid/obs'),
    ProcessMatch(proc, '#test', 'announce/test.js'),
    ProcessMatch(proc, '#senrio', 'announce/senrio.js'),
    ProcessMatch(proc, '#scanlime', 'announce/scanlime.js'),
    ProcessMatch(proc, '+ffm', 'ffmpeg'),
]

screensaver = [
    ClockWidget(),
]

vfd = mi6k.Device().vfd

def widgetTexts(w):
    return filter(None, map(str, w))

def wrapScreen(texts):
    return '\n'.join(textwrap.wrap(' '.join(texts), mi6k.CenturyVFD.width)[:mi6k.CenturyVFD.lines])

while 1:
    dashTexts = widgetTexts(dash)
    screensaverTexts = widgetTexts(screensaver)
    vfd.setBrightness(brightnessLevels[len(dashTexts) != 0])
    vfd.writeScreen(wrapScreen(dashTexts + screensaverTexts))
