#!/usr/bin/env python2

import qmp
import sys

def onlinecpu():
    import numa

    o_cpus = []
    for node in range(0,numa.get_max_node()+1):
        for cpu in sorted(numa.node_to_cpus(node)):
            o_cpus.append(cpu)

    return o_cpus


def pin_proc(pid, core):
    import psutil

    try:
        psutil.Process(pid).cpu_affinity([core])
    except ValueError as e:
        print >> sys.stderr, e
        sys.exit(1)


# 1 --> port number
# 2 --> number of vcpus

query = qmp.QMPQuery("localhost:%s" % (sys.argv[1]))
response = query.cmd("query-cpus")['return']
o_cpus = [x for x in range(int(sys.argv[2]))]

for i in range(int(sys.argv[2])):
    pin_proc(int(response[i]['thread_id']), o_cpus[i])
