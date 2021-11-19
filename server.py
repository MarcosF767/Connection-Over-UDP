#!/usr/bin/env python3

import sys
import argparse
import socket
import signal

import confundo

# for testing, replace socket.socket with confundo.Socket()
# or just use the reference server (check Piazza or consult the instructor)

# the server can only work in a single threaded mode, one client at a time (no parallel,
# neither concurrent nor threaded---simplifications in the socket implementation)

# Other than that, standard socket interface should work

def start():
    pass

if __name__ == '__main__':
    start()
