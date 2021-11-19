# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
# Copyright 2019 Alex Afanasyev
#

from .header import Header

class Packet(Header):
    '''Abstraction to handle the whole Confundo packet (e.g., with payload, if present)'''

    def __init__(self, payload=b"", isDup=False, **kwargs):
        super(Packet, self).__init__(**kwargs)
        self.payload = payload
        self.isDup = isDup # only for printing flags

    def decode(self, fullPacket):
        super(Packet, self).decode(fullPacket[0:12])
        self.payload = fullPacket[12:]
        return self

    def encode(self):
        return super(Packet, self).encode() + self.payload
