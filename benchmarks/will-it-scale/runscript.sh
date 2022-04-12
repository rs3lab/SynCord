#!/bin/zsh

workload=(mmap1 mmap2 lock1 lock2 page_fault1 page_fault2)

for wl in ${workload[@]}
do
	sudo mount -t tmpfs -o size=10G tmpfs /mnt/tmpfs/

	echo "# stock : $wl"
	python runtest.py $wl
	
	sudo umount /mnt/tmpfs/
done
