#!/bin/bash

result_dir=$1
DB_BENCH=./leveldb-1.20/out-static/db_bench
cores=(1 2 4 8 16 28 56 84 112 140 168 196 224)
DB_PATH=/tmp/db

# Create result directory
mkdir $result_dir

for c in ${cores[@]}
do
	# sudo mount -t tmpfs -o size=10G tmpfs $DB_PATH
	# Create DB with db_bench
	$DB_BENCH --db=$DB_PATH --benchmarks=fillseq --threads=1
	# sync
	# sudo ./bin/drop-caches
	$DB_BENCH --benchmarks=readrandom --use_existing_db=1 --db=$DB_PATH --threads=$c | tee ./$result_dir/readrandom.$c

	sudo rm -rf $DB_PATH/*
	# sudo umount $DB_PATH
	sleep 5
done

