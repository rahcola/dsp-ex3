import sys
import time
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

def write_config(config, path):
    with open(path, "w") as f:
        f.write("\n".join(config))
        f.write("\n")

def start_nodes(host, f, t, dim, time, config_path):
    prefix = sys.path[0]
    args = "{0} {1} {2} {3} {4} {5}".format(f, t, dim, time, prefix, config_path)
    remote_cmd =  prefix + "/start_nodes.sh " + args
    cmd = ["ssh", "-4", "-A", "-q", host, remote_cmd]
    return subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            universal_newlines = True)

def main(args):
    dim = int(args[1])
    tt = float(args[2])
    config_path = args[3]
    hosts_path = args[4]
    hosts = lines(hosts_path)
    d = distribute(dim, hosts)
    write_config(build_config(d), config_path)
    procs = []
    for host, f, t in d:
        time.sleep(0.1)
        procs.append(start_nodes(host, f, t, dim, tt, config_path))
    for p in procs:
        p.wait()
        print(p.communicate()[0].strip())

if __name__ == "__main__":
    main(sys.argv)
