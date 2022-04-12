#!/usr/bin/python

import time
import subprocess
import sys
import os
import re

data_points = [1,2,4,8]
# data_points = [1,2,4,8,16,28,56,84,112,140,168,196,224]

class linux_stat():
    def __init__(self, procstat='/proc/stat'):
        fd = open(procstat, 'r');
        for line in fd.readlines():
            arr = line.split()
            if arr[0] != 'cpu':
                continue

            self.user = int(arr[1])
            self.nice = int(arr[2])
            self.system = int(arr[3])
            self.idle = int(arr[4])
            self.iowait = int(arr[5])
            self.irq = int(arr[6])
            self.softirq = int(arr[7])
            self.steal = 0
            self.guest = 0
            self.guest_nice = 0
            if len(arr) > 8:
                self.steal = int(arr[8])
            if len(arr) > 9:
                self.guest = int(arr[9])
            if len(arr) > 10:
                self.guest_nice = int(arr[10])

            break
        fd.close()

    def idle_fraction(self, prev):
        busy = self.user + self.nice + self.system + self.irq + self.softirq + self.steal + self.guest + self.guest_nice
        idle = self.idle + self.iowait

        if prev:
            busy = busy - (prev.user + prev.nice + prev.system + prev.irq + prev.softirq + prev.steal + prev.guest + prev.guest_nice)
            idle = idle - (prev.idle + prev.iowait)

        if (idle + busy) == 0:
            return 0

        return 1.0 * idle / (idle + busy)


duration=5

if len(sys.argv) != 2:
    print >> sys.stderr, 'Usage: runtest.py <testcase>'
    sys.exit(1)
cmd = sys.argv[1]

nr_cores = int(subprocess.check_output("lscpu -e=cpu | wc -l", shell=True).strip().decode()) -1
nr_nodes = int(subprocess.check_output("lscpu -e=node | sort -u | wc -l", shell=True).strip().decode()) -1
cores_per_socket = nr_cores / nr_nodes

print "(num_cores, num_nodes, cores_per_socket) = (%d, %d, %d)" % (nr_cores, nr_nodes,
        cores_per_socket)

setarch = 'setarch linux64 -R'
try:
    retcode = subprocess.call(setarch + " /bin/true", shell=True)
except OSError, e:
    retcode = -1

if retcode != 0:
    setarch = ''
    print >> sys.stderr, 'WARNING: setarch -R failed, address space randomization may cause variability'

pipe = subprocess.Popen('uname -m', shell=True, stdout=subprocess.PIPE).stdout
arch = pipe.readline().rstrip(os.linesep)
pipe.close()

if arch == 'ppc64':
    pipe = subprocess.Popen('ppc64_cpu --smt 2>&1', shell=True, stdout=subprocess.PIPE).stdout
    smt_status = pipe.readline()
    pipe.close()
    if 'off' not in smt_status:
        print >> sys.stderr, 'WARNING: SMT enabled, suggest disabling'

print 'tasks,processes,processes_idle,threads,threads_idle,linear'
print '0,0,100,0,100,0'

for i in data_points:
    c = './build/%s_processes -t %d -s %d -n %d' % (cmd, i, duration, cores_per_socket)
    before = linux_stat()
    pipe = subprocess.Popen(setarch + ' ' + c, shell=True, stdout=subprocess.PIPE).stdout
    processes_avg = -1
    for line in pipe.readlines():
        if 'testcase:' in line:
            (testcase, val) = line.split(':')
            title = open(cmd + '.title', 'w')
            title.write(val)
            title.close()

        if 'average:' in line:
            (name, val) = line.split(':')
            processes_avg = int(val)
    pipe.close()
    after = linux_stat()
    processes_idle = after.idle_fraction(before) * 100

    c = './build/%s_threads -t %d -s %d -n %d' % (cmd, i, duration, cores_per_socket)
    before = linux_stat()
    pipe = subprocess.Popen(setarch + ' ' + c, shell=True, stdout=subprocess.PIPE).stdout
    threads_avg = -1
    for line in pipe.readlines():
        if 'average:' in line:
            (name, val) = line.split(':')
            threads_avg = int(val)
    pipe.close()
    after = linux_stat()
    threads_idle = after.idle_fraction(before) * 100

    if i == 1:
        linear = max(processes_avg, threads_avg)

    print '%d,%d,%0.2f,%d,%0.2f,%d' % (i, processes_avg, processes_idle, threads_avg, threads_idle, linear * i)
