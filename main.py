import select
import asyncore
import koorde
import socket
import time
import sys
from collections import deque

def parse_remotes(path, dimension):
    with open(path) as f:
        remotes = {}
        for l in f:
            id, host, port = l.split(" ")
            id = koorde.Id(int(id), dimension)
            remotes[id] = (host, int(port))
        return remotes

def loop(timeout=30.0, use_poll=False, map=None, for_time=None):
    if map is None:
        map = asyncore.socket_map

    if use_poll and hasattr(select, 'poll'):
        poll_fun = asyncore.poll2
    else:
        poll_fun = asyncore.poll

    if for_time is None:
        while map:
            poll_fun(timeout, map)

    else:
        start = time.time()
        while map and time.time() - start < for_time:
            poll_fun(timeout, map)

class P():
    def __init__(self, id, remotes):
        self.id = id
        self.received = {}
        self.messages = deque(remotes.keys())

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, id):
        if id not in self.received:
            hops = len(data[:-4])
            self.received[id] = hops
            print(id, self.id, hops)

    def writable(self):
        return True

    def handle_write(self):
        id = self.messages.popleft()
        self.transport.sendto(b"PING", id)
        self.messages.append(id)

def main(args):
    dimension = int(args[1])
    id = koorde.Id(int(args[2]), dimension)
    t = float(args[3])
    remotes = parse_remotes(args[4], dimension)
    node = koorde.KoordeOverDatagram(P(id, remotes), id, remotes)
    node.connect()
    loop(for_time=t)

if __name__ == "__main__":
    main(sys.argv)
