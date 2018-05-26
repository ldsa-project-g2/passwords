#!/usr/bin/env python3
import sys


SPARKFILE = "/usr/local/spark/spark-2.3.0-bin-hadoop2.7/conf/slaves"

if __name__ == '__main__':
    desired_workers = int(sys.argv[1])

    active = []
    inactive = []

    with open(SPARKFILE, "r") as fp:
        for hostname in (l.strip() for l in fp if l.strip()):
            hostname = hostname.replace("#", "").strip()

            if hostname == "group-2-project-1":
                active.append(hostname)
                continue

            if len(active) > desired_workers:
                inactive.append(hostname)
            else:
                active.append(hostname)

    with open(SPARKFILE, "w") as fp:
        for hostname in active:
            fp.write(hostname + "\n")
        for hostname in inactive:
            fp.write("# {}\n".format(hostname))
