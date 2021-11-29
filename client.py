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
        self.connId = connId

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
        if(self.cwnd < self.ssthresh):
            self.cwnd += MTU
        else:
            self.cwnd += (MTU ** 2) / self.cwnd

    def on_timeout(self):
        self.ssthresh = self.cwnd / 2
        self.cwnd = MTU

    def __str__(self):
        return f"cwnd:{self.cwnd} ssthreash:{self.ssthresh}"
    
    
    
    
    
    
    
import argparse
import os
import socket
import sys
import time
import math

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()

PORT = args.port
HOST = args.host
FILE = args.file
GLOBAL_TIMEOUT = 10.0
MTU=412



def start():
    
    remoteAddr = 0
    lastFromAddr = 0
    connId = 0
    base = 77
    seqNum = base
    inSeq = 0
    inAck = 0
    nDupAcks = 0
    synReceived = False
    finReceived = False
    inBuffer = b""
    outBuffer = b""
    cwnd = CwndControl()
    endedAt = 0
    
    '''***********************************************************************'''
    def send(packet, remoteAddr, lastFromAddr):
        if remoteAddr:
            sock.sendto(packet.encode(), remoteAddr)
        else:
            sock.sendto(packet.encode(), lastFromAddr)
        print(format_line("SEND",  packet, cwnd.cwnd, cwnd.ssthresh))
        
        
    def format_line(command, pkt, cwnd, ssthresh):
        s = f"{command} {pkt.seqNum} {pkt.ackNum} {pkt.connId} {int(cwnd)} {ssthresh}"
        if pkt.isAck: s = s + " ACK"
        if pkt.isSyn: s = s + " SYN"
        if pkt.isFin: s = s + " FIN"
        if pkt.isDup: s = s + " DUP"
        return s
    
    def recv(lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer, base):
        now = time.time()
        try:
            (inPacket, lastFromAddr) = sock.recvfrom(1024)
        except socket.error as e:
            seqNum = base
            cwnd.on_timeout()
            return (None, lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer)

        inPkt = Packet().decode(inPacket)
        inAck = inPkt.ackNum    ##########################################
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
                sys.stderr.write("Receiving data before SYN received")
                sys.exit(1)

            if finReceived:
                raise RuntimeError("Received data after getting FIN (incoming connection closed)")
                sys.stderr.write("Received data after getting FIN (incoming connection closed)")
                sys.exit(1)

            if inSeq == inPkt.seqNum: # all previous packets has been received, so safe to advance
                inSeq += len(inPkt.payload)
                inBuffer += inPkt.payload
            else:
                # don't advance, which means we will send a duplicate ACK
                pass

            outPkt = Packet(seqNum=seqNum, ackNum=inSeq, connId=connId, isAck=True)

        if outPkt:
            send(outPkt, remoteAddr, lastFromAddr)

        return (inPkt, lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer)
            

    def sendData(data, base, seqNum, outBuffer, connId, lastFromAddr, inSeq, inAck, synReceived, finReceived, inBuffer, nDupAcks, cwnd, endedAt):
        '''
        This is one of the methods that require fixes.  Besides the marked place where you need
        to figure out proper updates (to make basic transfer work), this method is the place
        where you should initate congestion control operations.   You can either directly update cwnd, ssthresh,
        and anything else you need or use CwndControl class, up to you.  There isn't any skeleton code for the
        congestion control operations.  You would need to update things here and in `format_msg` calls
        in this file to properly print values.
        '''

        outBuffer += data

        startTime = time.time()
        while len(outBuffer) > 0:
            pkt = None
            toSend = None
            if((seqNum+MTU) > 40000):
                #index = 40000 - seqNum
                toSend = outBuffer[:MTU]#index]
                pkt = Packet(seqNum=seqNum, connId=connId, payload=toSend)
                seqNum = seqNum + 412 - 40000
                endedAt += base
                base = seqNum
            else:
                toSend = outBuffer[:MTU]
                pkt = Packet(seqNum=seqNum, connId=connId, payload=toSend)
                if((base) == seqNum):
                    seqNum += len(toSend)
                
            send(pkt, remoteAddr, lastFromAddr)

            (pkt, lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer) = recv(lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer, base)  
                    # if within RTO we didn't receive packets, things will be retransmitted
            if pkt and pkt.isAck:
                advanceAmount = pkt.ackNum - base- endedAt
                if advanceAmount == 0:
                    print("Here")
                    nDupAcks += 1
                else:
                    nDupAcks = 0
                    cwnd.on_ack(0)
                    startTime = time.time()

                outBuffer = outBuffer[advanceAmount:]
                base = seqNum
            if time.time() - startTime > GLOBAL_TIMEOUT:
                raise RuntimeError("timeout")
                sock.close()
                exit(1)

        return (len(data), base, seqNum, outBuffer, connId, lastFromAddr, inSeq, inAck, synReceived, finReceived, inBuffer, nDupAcks, cwnd, endedAt)
            
            
            
            
            
            
            
            
            
            
            
    try:
        sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.settimeout(0.5)
        remote = socket.getaddrinfo(HOST, PORT, family=socket.AF_INET, type=socket.SOCK_DGRAM)
        (family, type, proto, canonname, sockaddr) = remote[0]

        remoteAddr = sockaddr


        #self.sendSynPacket()
        synPkt = Packet(seqNum=seqNum, connId=connId, isSyn=True)
        seqNum = seqNum + 1
        send(synPkt, remoteAddr, lastFromAddr)

        #self.expectSynAck()
        startTime = time.time()
        while True:
            (pkt, lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer) = recv(lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer, base)
            if pkt and pkt.isAck and pkt.ackNum == seqNum:
                base = seqNum
                break
            if time.time() - startTime > GLOBAL_TIMEOUT:
                raise RuntimeError("timeout")

        #Send files
        with open(FILE, "rb") as f:
            data = f.read(50000)
            while data:
                total_sent = 0
                while total_sent < len(data):
                    (sent, base, seqNum, outBuffer, connId, lastFromAddr, inSeq, inAck, synReceived, finReceived, inBuffer, nDupAcks, cwnd, endedAt) = sendData(data[total_sent:], base, seqNum, outBuffer, connId, lastFromAddr, inSeq, inAck, synReceived, finReceived, inBuffer, nDupAcks, cwnd, endedAt)
                    total_sent += sent
                    data = f.read(50000)
        
        #self.sendFinPacket()
        synPkt = Packet(seqNum=seqNum, connId=connId, isFin=True)
        seqNum += 1
        send(synPkt, remoteAddr, lastFromAddr)
        
        
        
        #self.expectFinAck()
        startTime = time.time()
        while True:
            (pkt, lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer) = recv(lastFromAddr, connId, seqNum, inSeq, inAck, synReceived, finReceived, inBuffer, base)
            if pkt and pkt.isAck and pkt.ackNum == seqNum:
                base = seqNum
                break
            if time.time() - startTime > GLOBAL_TIMEOUT:
                return
        now = time.time()
        while True:
            try:
                (inPacket, lastFromAddr) = sock.recvfrom(1024)
                inPkt = Packet().decode(inPacket)
            except:
                inPkt = None
            if inPkt and inPkt.isFin and pkt.ackNum == seqNum:
                print(format_line("RECV", inPkt, cwnd.cwnd, cwnd.ssthresh))
                pak = Packet(seqNum=seqNum, ackNum=inSeq, connId=connId, isAck=True)
                send(pak, remoteAddr, lastFromAddr)
            elif inPkt:
                print(format_line("DROP", inPkt, cwnd.cwnd, cwnd.ssthresh))
            if((time.time()) - now >= 5):
                break
        
        
    except:
        sys.stderr.write(f"ERROR: File transfer failed")
        sys.exit(1)
    finally:
        sock.close()
        exit(0)
    
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