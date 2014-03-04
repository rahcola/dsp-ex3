#!/usr/bin/env python3

# Jani Rahkola, 01360669

import sys
import argparse

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

parser = argparse.ArgumentParser(
    description = "Generates start_overlay.py configurations."
)
parser.add_argument("dimension",
                    metavar = "DIMENSION",
                    type = int,
                    help = "dimension of the overlay")
parser.add_argument("hosts_file",
                    metavar = "HOSTS",
                    type = str,
                    help = "path to a file with hostnames, one per line")

def main(args):
    hosts = lines(args.hosts_file)
    d = distribute(args.dimension, hosts)

    for s in (build_config(distribute(args.dimension, hosts))):
        print(s)

if __name__ == "__main__":
    main(parser.parse_args())
