# Jani Rahkola, 013606996

import time
import socket
import asyncore
import struct
import sys
import collections
from random import choice

def resolve(host, port, c = 5):
    try:
        addr = socket.getaddrinfo(host, port,
                                  family = socket.AF_INET,
                                  type = socket.SOCK_DGRAM)[0]
        return addr[4]
    except:
        if c > 0:
            time.sleep(6 - c)
            print(socket.gethostname(), "retrying resolve for", host,
                  file=sys.stderr)
            return resolve(host, port, c - 1)
        else:
            print("could not resolve", host,
                  file=sys.stderr)
            sys.exit(1)

class Id():
    def __init__(self, id, length):
        self.id = id & ~(~0 << length)
        self.length = length
        self.msb = (id >> (length - 1)) & 1

    def __add__(self, i):
        if isinstance(i, int):
            return Id(self.id + i, self.length)
        else:
            raise NotImplemented

    def __lshift__(self, i):
        if isinstance(i, int) and i >= 0:
            if i == 0:
                return self
            return Id(self.id << i, self.length)
        else:
            raise NotImplemented

    def __rshift__(self, i):
        if isinstance(i, int) and i >= 0:
            if i == 0:
                return self
            return Id(self.id >> i, self.length)
        else:
            raise NotImplemented

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return bin(self.id)

    def __index__(self):
        return self.id

class Header():
    fmt = ">BQQQ"
    size = struct.calcsize(fmt)

    def __init__(self, dimension, sender, receiver, route):
        self.dimension = dimension
        self.sender = sender
        self.receiver = receiver
        self.route = route

    def __str__(self):
        return (str(self.sender) +
                " " + str(self.receiver) +
                " " + str(self.route))

    def __bytes__(self):
        return struct.pack(Header.fmt,
                           self.dimension,
                           self.sender,
                           self.receiver,
                           self.route)

    @classmethod
    def from_bytes(cls, bytes):
        dimension, sender, receiver, route = struct.unpack_from(Header.fmt, bytes)
        return cls(dimension,
                   Id(sender, dimension),
                   Id(receiver, dimension),
                   Id(route, dimension))

class KoordeOverDatagram(asyncore.dispatcher):
    def __init__(self, protocol, id, remotes):
        asyncore.dispatcher.__init__(self)
        self.protocol = protocol
        self.id = id
        self.addr = remotes[id]
        self.upstream = [resolve(*remotes[id << 1]),
                         resolve(*remotes[(id << 1) + 1])]

    def __parse_header(self, data):
        return (Header.from_bytes(data), data[Header.size:])

    def __relay(self, data, header):
        addr = self.getnameinfo(header.route)
        header.route = header.route << 1
        self.buffer.append((bytes(header) + b"*" + data, addr))

    def connect(self):
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", self.addr[1]))
        self.rcvbuf = self.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        self.pending = set(self.upstream)
        self.buffer = collections.deque()
        self.priority_buffer = collections.deque()

    def readable(self):
        return True

    def handle_read(self):
        data, addr = self.recvfrom(self.rcvbuf)
        if data == b"SYN":
            if (b"ACK", addr) not in self.priority_buffer:
                self.priority_buffer.append((b"ACK", addr))
        elif data == b"ACK":
            if addr in self.pending:
                self.pending.remove(addr)
                if len(self.pending) == 0:
                    self.protocol.connection_made(self)
        else:
            header, data = self.__parse_header(data)
            if header.receiver == self.id:
                self.protocol.datagram_received(data, header.sender)
            else:
                self.__relay(data, header)

    def writable(self):
        for addr in self.pending:
            if (b"SYN", addr) not in self.priority_buffer:
                self.priority_buffer.append((b"SYN", addr))
        return (len(self.priority_buffer) > 0 or
                len(self.buffer) > 0 or
                self.protocol.writable())

    def handle_write(self):
        if len(self.priority_buffer) > 0:
            self.socket.sendto(*self.priority_buffer.popleft())
            return

        if len(self.pending) == 0 and self.protocol.writable():
            self.protocol.handle_write()

        if len(self.buffer) > 0:
            self.socket.sendto(*self.buffer.popleft())

    # transport

    def getnameinfo(self, id):
        return self.upstream[id.msb]

    def sendto(self, data, id):
        addr = self.getnameinfo(id)
        header = Header(self.id.length, self.id, id, id << 1)
        self.buffer.append((bytes(header) + b"*" + data, addr))
