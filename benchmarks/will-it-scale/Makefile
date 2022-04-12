CFLAGS=-Wall -O2 -g -pg

ifdef wl
	workload=tests/$(wl).c
else
	workload=$(wildcard tests/*.c)
endif

processes := $(patsubst tests/%.c,%_processes,$(workload))
threads := $(patsubst tests/%.c,%_threads,$(workload))

all: build_dir | processes threads

processes: $(processes)

threads: $(threads)

posix_semaphore1_processes_FLAGS=-lpthread

build_dir:
	mkdir -p build

$(processes): %_processes: tests/%.o main.c
	$(CC) $(CFLAGS) main.c $< $($@_FLAGS) $(LDFLAGS) -o build/$@

$(threads): %_threads: tests/%.o main.c
	$(CC) -DTHREADS $(CFLAGS) main.c $< -pthread $(LDFLAGS) -o build/$@

clean:
	rm -f tests/*.o
	rm -rf build
