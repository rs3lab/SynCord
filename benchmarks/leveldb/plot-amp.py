import os
import string
import sys
import re

cores = [1,2,4,8,16,28,56,84,112,140,168,196,224]

if __name__ == '__main__':
    dir = sys.argv[1]

    print("#num_threads, fast, slow, tot ops/s")

    for i in cores:
        dir_path = "./"+dir+"/readrandom."+str(i)
        #  print(dir_path)
        stats = []
        with open(dir_path) as f:
            lines = f.readlines()

            for line in lines:
                if line.startswith('readrandom'):
                    run = re.findall('[0-9.]+', line)
                    stats.append(run[0])

            stats.append(0)

            print("{}, {}, {}, {}".format(i, stats[0], stats[1], stats[2]))
