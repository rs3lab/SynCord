#!/bin/bash

import os
import sys
import random
import string
import shutil

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

if __name__ == '__main__':

    # Create three directories: src_empty, dst_empty, dst_N_files.
    # dst_dirty has a million empty files
    # each file name is 36 characters.
    num_files = sys.argv[1]

    mkdir('src_empty', 0)
    mkdir('dst_empty', 0)
    mkdir('dst_'+num_files+'_files', int(num_files))
