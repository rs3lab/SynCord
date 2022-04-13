import os
import sys
import re

cores = [1,2,4,8,14,28,56,84,112,140,168,196,224]

print("CORE, RUNTIME")
for core in cores:
    dir_path = sys.argv[1]+"/result."+str(core)

    try:
        with open(dir_path) as f:
            lines = f.read()
            runtime = re.findall('Real:\s+(\d+)', lines)

            print('%3d, %s' % (core,runtime[0]))
    except Exception as e:
        print()

