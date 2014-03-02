import asyncore
import koorde
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

class P():
    def __init__(self, id, remotes):
        self.id = id
        self.received = {}
        self.messages = deque(remotes.keys())

    def connection_made(self, transport):
        self.transport = transport
        self.last_sent = time.time()

    def datagram_received(self, data, id):
        if id not in self.received:
            hops = len(data[:-4])
            self.received[id] = hops
            print(id, self.id, hops)

    def writable(self):
        return time.time() - self.last_sent > 0.1

    def handle_write(self):
        id = self.messages.popleft()
        self.transport.sendto(b"PING", id)
        self.messages.append(id)
        self.last_sent = time.time()

def main(args):
    dimension = int(args[1])
    id = koorde.Id(int(args[2]), dimension)
    remotes = parse_remotes(args[3], dimension)
    node = koorde.KoordeOverDatagram(P(id, remotes), id, remotes)
    node.connect()
    asyncore.loop(timeout = 0.1)

if __name__ == "__main__":
    main(sys.argv)
