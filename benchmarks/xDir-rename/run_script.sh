#!/bin/zsh

duration=30
# cores=(2 4 8 16 28 56 84 112 140 168 196 224)
cores=(2 4)

if [ -n $1 ]
then
	policydir = $1
else
	policydir = default
fi

mkdir -p results
mkdir ./results/$policydir

for var in ${cores[@]}
do
	# install policy
	sudo $policydir/eBPFGen/scl_acqed_lock
	sudo $policydir/eBPFGen/scl_cmp
	sudo $policydir/eBPFGen/scl_cont
	sudo $policydir/eBPFGen/scl_release_lock

	sudo insmod $policydir/LivePatchGen/livepatch-concord.ko
	sleep 5

	python3 run_bench.py 1000000 $duration $(($var/2)) $(($var/2)) | tee ./results/$policydir/result.$var

	sudo ~/SynCord/scripts/uninstall_policy.sh
	sleep 10
done	
