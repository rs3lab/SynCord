#!/usr/bin/bash

if [ $# -ne 6 ]
then
	echo "usage $0 num_cpu thread_per_core core_per_socket [amp|restore] fast_freq slow_freq"
	exit 1
fi

num_cpu=$1
thread_per_core=$2
core_per_socket=$3
action=$4
fast_freq=$5
slow_freq=$6

start_cpu=0
half_core_per_socket=$(($core_per_socket/2))

change_cpu_freq()
{
	local cpu=$1
	local freq=$2

	sudo cpupower -c $cpu frequency-set -u $freq
	sudo cpupower -c $cpu frequency-set -d $freq
}


for i in `seq $start_cpu $(($num_cpu-1))`
do

	if [ $action == "amp" ]
	then
		offset=$(($i % $core_per_socket))

		if [ $offset -lt $half_core_per_socket ]
		then
			change_cpu_freq $i $fast_freq
		else
			change_cpu_freq $i $slow_freq
		fi

	elif [ $action == "restore" ]
	then
		sudo cpupower -c $i frequency-set -u $fast_freq
		sudo cpupower -c $i frequency-set -d $slow_freq
	fi
done
