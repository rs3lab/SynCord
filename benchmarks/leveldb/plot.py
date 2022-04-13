#!/usr/bin/env python3

import os
import string
import sys
import re

if __name__ == '__main__':
    dir = sys.argv[1]
    core = []

    filenames = next(os.walk(dir), (None, None, []))[2]

    for filename in filenames:
        core.append(int(os.path.splitext(filename)[1][1:]))

    core.sort()

    print("#num_threads, fast, slow, tot ops/s")
    for i in core:
        file = "./"+dir+"/readrandom."+str(i)
        #  print(dir_path)
        stats = []
        with open(file) as f:
            lines = f.readlines()

            for line in lines:
                if line.startswith('readrandom'):
                    run = re.findall('[0-9.]+', line)
                    stats.append(run[0])

            stats.append(0)

            print("{}, {}, {}, {}".format(i, stats[0], stats[1], stats[2]))
