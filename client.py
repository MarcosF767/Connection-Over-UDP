import struct

class Packet():
    '''Abstraction to handle the whole Confundo packet (e.g., with payload, if present)'''

    def __init__(self, payload=b"", isDup=False, seqNum=0, ackNum=0, connId=0, isAck=False, isSyn=False, isFin=False):
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.connId = connId
        self.isAck = isAck
        self.isSyn = isSyn
        self.isFin = isFin
        self.payload = payload
        self.isDup = isDup # only for printing flags
        self.connectionID = connectionID

    def decode(self, fullPacket):
        (self.seqNum, self.ackNum, self.connId, flags) = struct.unpack("!IIHH", fullPacket[0:12])
        self.isAck = flags & (1 << 2)
        self.isSyn = flags & (1 << 1)
        self.isFin = flags & (1)
        self.payload = fullPacket[12:]
        return self

    def encode(self):
        flags = 0
        if self.isAck:
            flags = flags | (1 << 2)
        if self.isSyn:
            flags = flags | (1 << 1)
        if self.isFin:
            flags = flags | (1)
        pay = struct.pack("!IIHH",
                           self.seqNum, self.ackNum,
                           self.connId, flags)
        return pay + self.payload


class CwndControl:
    '''Interface for the congestio control actions'''

    def __init__(self):
        self.cwnd = 412
        self.ssthresh = 12000

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

    
    
    
    

    
    
    
    
    
    
    
import argparse
import os
import socket
import sys

import confundo

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()

PORT = args.port
HOST = args.host
FILE = args.file
GLOBAL_TIMEOUT = 10.0

def start():
    
    remoteAddr = 0
    lastFromAddr = 0
    connId = 0
    seqNum = 77
    inSeq = 0
    synReceived = False
    finReceived = False
    inBuffer = b""
    cwnd = CwndControl()
    
    '''***********************************************************************'''
    def send(packet):
        if remoteAddr:
            sock.sendto(packet.encode(), remoteAddr)
        else:
            sock.sendto(packet.encode(), lastFromAddr)
        print(format_line("SEND",  packet, cwnd.cwnd, cwnd.ssthresh))
        
    def recieve():
        try:
            (inPacket, lastFromAddr) = self.sock.recvfrom(1024)
        except socket.error as e:
            return None
        
    def format_line(command, pkt, cwnd, ssthresh):
        s = f"{command} {pkt.seqNum} {pkt.ackNum} {pkt.connId} {int(cwnd)} {ssthresh}"
        if pkt.isAck: s = s + " ACK"
        if pkt.isSyn: s = s + " SYN"
        if pkt.isFin: s = s + " FIN"
        if pkt.isDup: s = s + " DUP"
        return s
    
    def recv():
        try:
            (inPacket, lastFromAddr) = sock.recvfrom(1024)
        except socket.error as e:
            return None

        inPkt = Packet().decode(inPacket)
        print(format_line("RECV", inPkt, cwnd.cwnd, cwnd.ssthresh))

        outPkt = None
        if inPkt.isSyn:
            inSeq = inPkt.seqNum + 1
            if inPkt.connId != 0:
                connId = inPkt.connId
            synReceived = True

            outPkt = Packet(seqNum=seqNum, ackNum=inSeq, connId=connId, isAck=True)

        elif inPkt.isFin:
            if inSeq == inPkt.seqNum: # all previous packets has been received, so safe to advance
                inSeq = inSeq + 1
                finReceived = True
            else:
                # don't advance, which means we will send a duplicate ACK
                pass

            outPkt = Packet(seqNum=seqNum, ackNum=inSeq, connId=connId, isAck=True)
            
        elif len(inPkt.payload) > 0:
            if not synReceived:
                raise RuntimeError("Receiving data before SYN received")

            if finReceived:
                raise RuntimeError("Received data after getting FIN (incoming connection closed)")

            if inSeq == inPkt.seqNum: # all previous packets has been received, so safe to advance
                inSeq += len(inPkt.payload)
                inBuffer += inPkt.payload
            else:
                # don't advance, which means we will send a duplicate ACK
                pass

            outPkt = Packet(seqNum=seqNum, ackNum=inSeq, connId=connId, isAck=True)

        if outPkt:
            self._send(outPkt)

        return inPkt
            

    
            
            
            
            
            
    
    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    remote = socket.getaddrinfo(HOST, PORT, family=socket.AF_INET, type=socket.SOCK_DGRAM)
    (family, type, proto, canonname, sockaddr) = remote[0]
    
    remoteAddr = sockaddr


    #self.sendSynPacket()
    synPkt = Packet(seqNum=seqNum, connId=connId, isSyn=True)
    seqNum = seqNum + 1
    send(synPkt)

    #self.expectSynAck()
    startTime = time.time()
    while True:
        pkt = recv()
        if pkt and pkt.isAck and pkt.ackNum == self.seqNum:
            self.base = self.seqNum
            self.state = State.OPEN
            break
        if time.time() - startTime > GLOBAL_TIMEOUT:
            self.state = State.ERROR
            raise RuntimeError("timeout")
            
            
    with open(FILE, "rb") as f:
        data = f.read(50000)
        while data:
            total_sent = 0
            while total_sent < len(data):
                sent = sendData(data[total_sent:])
                total_sent += sent
                data = f.read(50000)
    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    
    '''************************************************************************'''
    
    
'''    try:
        with confundo.Socket() as sock:
            sock.connect((HOST, int(PORT)))

            with open(FILE, "rb") as f:
                data = f.read(50000)
                while data:
                    total_sent = 0
                    while total_sent < len(data):
                        sent = sock.send(data[total_sent:])
                        total_sent += sent
                        data = f.read(50000)
    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)'''

if __name__ == '__main__':
    start()
