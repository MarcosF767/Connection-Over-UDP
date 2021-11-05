# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
# Copyright 2019 Alex Afanasyev
#

from .common import *

class CwndControl:
    '''Interface for the congestio control actions'''

    def __init__(self):
        self.cwnd = 1.0 * MTU
        self.ssthresh = INIT_SSTHRESH

    def on_ack(self, ackedDataLen):
        #
        # IMPLEMENT this and call this method in approprite place inside confundo/socket.py
        #
        pass

    def on_timeout(self):
        #
        # IMPLEMENT this and call this method in approprite place inside confundo/socket.py
        #
        pass

    def __str__(self):
        return f"cwnd:{self.cwnd} ssthreash:{self.ssthresh}"
