import os
import string
import sys
import re

duration = 60
cores = [2,4,8,16,28,56,84,112,140,168,196,224]

cycle_per_sec = 2200000000

if __name__ == '__main__':
    dir = sys.argv[1]

    print("#bully_throughput, victim_throughput, total_throughput, fairness,\
            bully_holdtime, victim_holdtime")

    for i in cores:
        dir_path = "./"+dir+"/result."+str(i)
        #  print(dir_path)
        with open(dir_path) as f:
            lines = f.readlines()
            bully_throughput = 0
            victim_throughput = 0
            fairness = 0

            bully_holdtime = 0
            victim_holdtime = 0

            for line in lines:
                run = re.findall('[0-9.]+', line)

                if line.startswith('[b]'):
                    bully_throughput = bully_throughput + int(run[2])
                    bully_holdtime = bully_holdtime + int(run[1])
                elif line.startswith('[v]'):
                    victim_throughput = victim_throughput + int(run[2])
                    victim_holdtime = victim_holdtime + int(run[1])
                elif line.startswith('fairness'):
                    fairness=run[0]

            print("{:.0f}, {:.0f}, {:.0f}, {}, {:.2f}, {:.2f}".format(bully_throughput/duration,\
                victim_throughput/duration, \
                (bully_throughput+victim_throughput)/duration, fairness,
                float(bully_holdtime)/cycle_per_sec,
                float(victim_holdtime)/cycle_per_sec))


    print("#xsock-cnt, #acquired, avg_batch_size")
    for i in cores:
            dir_path = "./"+dir+"/profile."+str(i)

            try:
                with open(dir_path) as f:
                    lines = f.readlines()
                    parsed = lines[3].split()

                    if int(parsed[1]) == 0:
                        continue

                    xsock_cnt = parsed[1]
                    #  norm_xsock_cnt = float(parsed[1])/float(parsed[3]) * 100
                    avg_batch_size = parsed[4]

                    print(xsock_cnt, parsed[3], avg_batch_size)
            except Exception as e:
                break
                
