#!/bin/bash

policy_path='/home/sujin/policy/bravo'
hash_size=(128 256 512 1024 2048 4096)
N=(1 2 4 8 10 12)
core=(1 2 4 8 14 28 56 84 112 140 168 196 224)

result_dir=bravo-concord-ing
mkdir $result_dir

for h in ${hash_size[@]}
do
	if [ $h -lt $1 ];then
	continue
	fi
			
	for n in ${N[@]}
	do
		if [[ $h -le $1 && $n -lt $2 ]];then
		continue
		fi

		# insert policy
		${policy_path}/eBPFGen/bravo-hash-size-${h}/bravo-hash-size
		${policy_path}/eBPFGen/bravo-rbias-level-${n}/bravo-rbias-level
		sudo insmod ${policy_path}/LivePatchGen/stock-bravo/livepatch-concord.ko
		sleep 10 

		for c in ${core[@]}
		do
			# run
			echo "Hashsize = ${h}, N = ${n}"
			filename=concord-H${h}-N${n}-C${c}.csv
			./obj.default/app/wrmem.sf -p $c | tee ${result_dir}/${filename}

		done
		
		# clean
		sudo /home/sujin/clean.sh
		sleep 5 

	done
done
