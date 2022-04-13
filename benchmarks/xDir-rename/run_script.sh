#!/bin/zsh

duration=30
workload=(scl scl-numa scl-numa-backoff)
# workload=(scl_profiling scl-numa_profiling scl-numa-backoff_profiling)
# workload=(shfllock_profiling)
# workload=(shfllock)
cores=(2 4 8 16 28 56 84 112 140 168 196 224)
# cache=(16 32 64 128 256 512 1024)
cache=(64 128 256 512 1024)

for c in ${cache[@]}
do
	mkdir ./results/SCL-${c}C

	make clean
	make CACHELINE=${c} 

	for policy in ${workload[@]}
	do	
		mkdir ./results/SCL-${c}C/$policy

		for var in ${cores[@]}
		do
			sudo ./install.sh $policy
			sleep 5
			./scl_usage ${duration} $(($var/2)) $(($var/2)) | tee ./results/SCL-${c}C/$policy/result.$var
			# sudo ~/policy/get_profiling_result/get_bpflockstat | tee ./results/$policy/profile.$var

			sudo ./clean.sh
			sleep 10
			sudo rmmod livepatch_concord
		done	
	done
done
