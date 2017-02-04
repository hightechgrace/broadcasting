""" mi6k

Python module for the IEE Century Vacuum Fluorescent Display,
formerly written for the Media Infrawidget 6000 project.

"""
#
# Copyright (C) 2004 Micah Elizabeth Scott <micah@navi.cx>
# Released into the public domain; CC0 1.0 Universal
# https://creativecommons.org/publicdomain/zero/1.0/
#

import serial
import struct
from numpy import *


class CenturyVFD:
    width = 20
    lines = 2
    userDefinedCharacters = ''.join(map(chr, range(0xF6, 0x100)))

    def __init__(self, dev):
        self.dev = dev
        self.remainingUserChars = self.userDefinedCharacters

    def powerOn(self):
        pass

    def powerOff(self):
        pass

    def write(self, data):
        "Write a string, handling newlines"
        lines = data.split('\n')
        lastLine = lines[-1]
        for l in lines[:-1]:
            self.writeVFD(l)
            self.nl()
        self.writeVFD(lastLine)

    def writeVFD(self, data):
        self.dev.write(data)

    def cr(self):
        self.dev.write("\r")

    def lf(self):
        self.dev.write("\n")

    def nl(self):
        self.cr()
        self.lf()

    def clear(self):
        self.writeVFD(chr(0x15))

    def home(self):
        self.writeVFD(chr(0x16))

    def cursorOff(self):
        self.writeVFD(chr(0x0E))

    def writeScreen(self, data):
        """Write a complete screen of data, without clearing the screen.
           'data' is a string with newlines separating each line.
           """
        lines = data.split("\n")
        while len(lines)<self.lines:
            lines.append("")
        self.home()
        self.cursorOff()
        for l in lines:
            if len(l) < self.width:
                l += " " * (self.width - len(l))
            elif len(l) > self.width:
                l = l[:self.width]
            self.writeVFD(l)
        self.dev.flush()

    def writeLines(self, lines):
        """Write a complete screen of data, without clearing the screen.
           'lines' is a sequence of strings, one for each line, assumed
           to already be exactly the size of our VFD.
           """
        self.home()
        self.cursorOff()
        for l in lines:
            self.writeVFD(l)
        self.dev.flush()

    def writeArray(self, data):
        """write a complete screen of data from a Numeric array"""
        data = asarray(data).astype(uint8)
        self.home()
        self.cursorOff()
        self.writeVFD(data.tostring())
        self.dev.flush()

    def defineCharacter(self, char, data):
        """Set a user defined character from a 5x7 Numeric array"""

        # The VFD has a strange dot ordering, we swizzle our original
        # bitmap into an array ordered first by bit position then by byte
        data = asarray(data)
        bits = take(data.flat, ( (17, 13,  9,  5,  1),
                                 ( 0, 31, 27, 23, 19),
                                 (16, 12,  8,  4,  0),
                                 (34, 30, 26, 22, 18),
                                 (15, 11,  7,  3,  0),
                                 (33, 29, 25, 21,  0),
                                 (14, 10,  6,  2,  0),
                                 (32, 28, 24, 20,  0) ))

        # Pack this resulting array into bytes
        bytes = bits[0] + bits[1]*2 + bits[2]*4 + bits[3]*8 + bits[4]*16 + bits[5]*32 + bits[6]*64 + bits[7]*128

        # Convert to a command string and send it
        self.writeVFD(chr(0x18) + char + bytes.astype(uint8).tostring())

    def allocCharacter(self, data):
        """Store the given array into the next available user defined
           character, returning it.
           """
        char = self.remainingUserChars[0]
        self.remainingUserChars = self.remainingUserChars[1:]
        self.defineCharacter(char, data)
        return char

    def setBrightness(self, l, column=0xFF):
        """Set the brightness of one column, or by default the entire display. l should be in the range [0,1]"""
        self.writeVFD("\x19\x30" + chr(column) + chr(int((1-l) * 0x07)))

    def flush(self):
        self.dev.flush()


class Device:
    """Container for all hardware reachable through the mi6k interface.
       Device is a pattern to search for the device node with.
       """
    def __init__(self, devPattern="/dev/ttyUSB0"):
        self.dev = serial.Serial(devPattern, baudrate=19200)
        self.vfd = CenturyVFD(self.dev)
