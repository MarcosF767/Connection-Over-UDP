#!/usr/bin/env python3

import argparse
import os
import socket
import sys

import confundo

PORT = 54000#20001#54000
HOST = '131.94.128.43'#"127.0.0.1"#'131.94.128.43'
FILE = 'hello.txt'

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()
PORT = args.port
HOST = args.host
FILE = args.file

#PORT = 54000#20001#54000
#HOST = '131.94.128.43'#"127.0.0.1"#'131.94.128.43'
#FILE = 'hello.txt'


def start():
    try:
        with confundo.Socket(sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            sock.settimeout(10)
            sock.connect((HOST, int(PORT)))

            with open(FILE, "rb") as f:
                data = f.read(50000)
                while data:
                    total_sent = 0
                    while total_sent < len(data):
                        sent = sock.send(data[total_sent:])
                        total_sent += sent
                        data = f.read(50000)
                        
    except e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()