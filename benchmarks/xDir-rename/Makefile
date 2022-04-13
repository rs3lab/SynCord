.PHONY: default clean

default: benchmark

benchmark: benchmark.c
	gcc -o benchmark benchmark.c -lpthread

clean:
	rm -rf benchmark dst_empty src_empty
