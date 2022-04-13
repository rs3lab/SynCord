#!/bin/bash

if [ $# -lt 1 ] ;  then
  echo 'usage: ./run_test.sh <result_dir_name>'
  exit 1
fi

RESULT=$1
mkdir $RESULT $RESULT/wrmem.sf

for var in 1 2 4 8 14 28 56 84 112 140 168 196 224
do
        # ./obj/wc ./data/wc/300MB_1M_Keys.txt -p $var | tee ./$RESULT/wc/result.$var
        #
		# ./obj/wr ./data/wr/100MB_100K_Keys.txt -p $var | tee ./$RESULT/wr/100MB_100K_Keys.$var
		# ./obj/wr ./data/wr/100MB_1M_Keys.txt -p $var | tee ./$RESULT/wr/100MB_1M_Keys.$var
		# ./obj/wr ./data/wr/500MB.txt -p $var | tee ./$RESULT/wr/500MB.$var
		# ./obj/wr ./data/wr/800MB.txt -p $var | tee ./$RESULT/wr/800MB.$var

        # ./obj/app/wrmem -p $var | tee ./$RESULT/wrmem/result.$var
        ./obj/app/wrmem.sf -p $var | tee ./$RESULT/wrmem.sf/result.$var
done


