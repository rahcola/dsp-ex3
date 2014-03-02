#!/usr/bin/env python3

import sys

def lines(file):
    lines = []
    with open(file) as f:
        for l in f:
            lines.append(l.strip())
    return lines

def distribute(dim, hosts):
    n = 2 ** dim
    per_node = int(n / len(hosts))
    d = list(zip(hosts,
                 range(0, n, per_node),
                 range(per_node, n + 1, per_node)))
    l = d[-1]
    d[-1] = (l[0], l[1], n)
    return d

def build_config(distribution):
    return ["{0} {1} {2}".format(id, host, 8000 + id - f)
            for host, f, t in distribution
            for id in range(f, t)]

def main(args):
    dim = int(args[1])
    hosts_path = args[2]
    hosts = lines(hosts_path)
    d = distribute(dim, hosts)

    for s in (build_config(distribute(dim, hosts))):
        print(s)

if __name__ == "__main__":
    main(sys.argv)
