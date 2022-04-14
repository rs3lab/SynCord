#!/bin/bash

import os
import sys
import random
import string
import shutil
import argparse

def get_rand_str(len) -> str:
    letters = string.ascii_letters
    rand_str = ''.join(random.choice(letters) for i in range(len))
    return rand_str

def touch(filename):
    with open(filename, 'a'):
        os.utime(filename, None)

def mkdir(dirname, num_files):
    if num_files == 0 :
        try:
            # Create target Directory
            os.mkdir(dirname)
            print("Directory " , dirname ,  "created ")
        except FileExistsError:
            shutil.rmtree(dirname)
            os.mkdir(dirname)
            print("Directory " , dirname ,  "created again")
    else:
        try:
            os.mkdir(dirname)
            for i in range(num_files):
                touch('./'+dirname+'/'+get_rand_str(36))
            print("Directory ", dirname , "created")

        except FileExistsError:
            list = os.listdir(dirname)
            file_count = len(list)

            if file_count == num_files:
                print("Directory ", dirname , " already exist with ", file_count, " files")

            elif file_count < num_files:
                for i in range(num_files - file_count):
                    touch('./'+dirname+'/'+get_rand_str(36))
                print("Directory ", dirname , "created")

            elif file_count > num_files:
                for i in range(file_count - num_files):
                    os.remove(list[i])
                print("Directory ", dirname , "created")

def prepare_dir(num_files):
    # Create three directories: src_empty, dst_empty, dst_N_files.
    # dst_dirty has a million empty files
    # each file name is 36 characters.

    mkdir('src_empty', 0)
    mkdir('dst_empty', 0)
    mkdir('dst_'+num_files+'_files', int(num_files))

def turn_off_dir_index():

    ret = os.system("sudo tune2fs -l /dev/sdb2 | grep dir_index")

    if ret == 0 :
        print("disable dir_index...")
        os.system("sudo tune2fs -O ^dir_index /dev/sdb2")

def run_bench(num_files, duration, bully, victim):
    try:
        os.system("./benchmark src_empty dst_%d_files dst_empty %d %d %d", \
                num_files, duration, bully, victim)
    except:
        print("error")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'xDir benchmark creates 3 directories.\
        Two empty directory `src_empty`, `dst_empty`, and `dst_N_files` directory which has N empty files')
    parser.add_argument('n', help = 'the number of files to creat under `dst_N_files`')
    parser.add_argument('duration', help='duration in sec to run the benchmark')
    parser.add_argument('bully', help = 'the number of bully threads')
    parser.add_argument('victim', help = 'the number of victim threads')

    args = parser.parse_args()

    prepare_dir(args.n)

    turn_off_dir_index()

    run_bench(args.n, args.duration, args.bully, args.victim)
