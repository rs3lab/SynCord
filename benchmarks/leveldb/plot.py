import os
import string
import sys
import re

cores = [1,2,4,8,16,28,56,84,112,140,168,196,224]

if __name__ == '__main__':
    dir = sys.argv[1]

    print("#num_threads, ops/s")

    for i in cores:
        dir_path = "./"+dir+"/readrandom."+str(i)
        #  print(dir_path)
        with open(dir_path) as f:
            lines = f.readlines()

            for line in lines:
                if line.startswith('readrandom'):
                    run = re.findall('[0-9.]+', line)
                    print("{}, {}".format(i, run[0]))
