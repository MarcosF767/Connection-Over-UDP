# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
# Copyright 2019 Alex Afanasyev
#
# This program is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.

import struct

class Header:
    '''Abstraction to handle Confundo header'''

    def __init__(self, seqNum=0, ackNum=0, connId=0, isAck=False, isSyn=False, isFin=False):
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.connId = connId
        self.isAck = isAck
        self.isSyn = isSyn
        self.isFin = isFin

    def encode(self):
        flags = 0
        if self.isAck:
            flags = flags | (1 << 2)
        if self.isSyn:
            flags = flags | (1 << 1)
        if self.isFin:
            flags = flags | (1)
        return struct.pack("!IIHH",
                           self.seqNum, self.ackNum,
                           self.connId, flags)

    def decode(self, packet):
        (self.seqNum, self.ackNum, self.connId, flags) = struct.unpack("!IIHH", packet)
        self.isAck = flags & (1 << 2)
        self.isSyn = flags & (1 << 1)
        self.isFin = flags & (1)

    def __str__(self):
        s = f"{self.seqNum} {self.ackNum} {self.connId}"
        if self.isAck: s = s + " ACK"
        if self.isSyn: s = s + " SYN"
        if self.isFin: s = s + " FIN"
        return s

    def __repr__(self):
        return self.__str__()
