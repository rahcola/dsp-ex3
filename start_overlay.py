#!/usr/bin/env python3

import sys
import subprocess

def lines(file):
    lines = []
    with open(file) as f:
        for l in f:
            lines.append(l.strip())
    return lines

def distribute(dim, hosts):
    n = 2 ** dim
    per_node = int(n / len(hosts))
    f = 0
    d = []
    for host in hosts:
        d.append((host, f, min(f + per_node, n)))
        f += per_node
    return d

def build_config(distribution):
    c = []
    for host, f, t in distribution:
        for id in range(f, t):
            c.append("{0} {1} {2}".format(id, host, 8000 + id - f))
    return c

def write_config(config, path):
    with open(path, "w") as f:
        f.write("\n".join(config))
        f.write("\n")

def start_nodes(host, f, t, dim, time, config_path):
    prefix = sys.path[0]
    args = "{0} {1} {2} {3} {4} {5}".format(f, t, dim, time, prefix, config_path)
    remote_cmd =  prefix + "/start_nodes.sh " + args
    cmd = ["ssh", "-A", host, remote_cmd]
    return subprocess.Popen(cmd)

def main(args):
    dim = int(args[1])
    time = float(args[2])
    config_path = args[3]
    hosts_path = args[4]
    hosts = lines(hosts_path)
    d = distribute(dim, hosts)
    write_config(build_config(d), config_path)
    procs = []
    for host, f, t in d:
        procs.append(start_nodes(host, f, t, dim, time, config_path))
    for p in procs:
        p.wait()

if __name__ == "__main__":
    main(sys.argv)
