#!/usr/bin/env python3

# Jani Rahkola, 013606996

import os
import sys
import time
import math
import argparse
import itertools
import subprocess

def read_config(file):
    config = []
    with open(file) as f:
        for l in f:
            id, host, port = l.strip().split(" ")
            config.append((id, host))
    return config

def parse_config(config):
    config.sort(key = lambda t: t[1])
    return [(host, " ".join([id for id, _ in nodes]))
            for host, nodes in itertools.groupby(config, key = lambda t: t[1])]

def remote_cmds(config, config_path, dim, timeout):
    prefix = os.path.dirname(os.path.abspath(__file__))
    template = "cd {0}; ./start_nodes.sh '{1}' {2} {3} {4}"
    return [(host, template.format(prefix, ids, dim, timeout, config_path))
            for host, ids in config]

def start_node(host, remote_cmd):
    return subprocess.Popen(["ssh", "-A", host, remote_cmd],
                            stdout = subprocess.PIPE,
                            universal_newlines = True)

parser = argparse.ArgumentParser(
    description = "Starts the overlay on remote hosts."
)
parser.add_argument("timeout",
                    metavar = "TIMEOUT",
                    type = int,
                    help = "how long to run a single node")
parser.add_argument("config_file",
                    metavar = "CONFIG",
                    type = str,
                    help = "path to a configuration file, generated by generate_config.py")

def main(args):
    timeout = args.timeout
    config_path = args.config_file
    config = read_config(config_path)
    dim = int(math.log(len(config), 2))
    config = parse_config(config)

    procs = []
    for host, remote_cmd in remote_cmds(config, config_path, dim, timeout):
        procs.append(start_node(host, remote_cmd))
        time.sleep(0.5)

    terminate = False
    for p in procs:
        if terminate:
            p.terminate()
        else:
            print(p.communicate()[0].strip())
            if p.returncode != 0:
                terminate = True

if __name__ == "__main__":
    main(parser.parse_args())
