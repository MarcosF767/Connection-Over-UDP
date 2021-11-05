

def format_line(command, pkt, cwnd, ssthresh):
    s = f"{command} {pkt.seqNum} {pkt.ackNum} {pkt.connId} {int(cwnd)} {ssthresh}"
    if pkt.isAck: s = s + " ACK"
    if pkt.isSyn: s = s + " SYN"
    if pkt.isFin: s = s + " FIN"
    if pkt.isDup: s = s + " DUP"
    return s
