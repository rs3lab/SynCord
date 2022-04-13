#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <pthread.h>
#include <errno.h>
#include <string.h>
#include "bench.h"
#include "lib/cpumap.h"
#include "lib/profile.h"

static struct {
    volatile int start;
    union {
	struct {
	    void *buf;
	    volatile int ready;
	    volatile uint64_t cycles;
	} v;
	char __pad[JOS_CLINE];
    } state[JOS_NCPU] __attribute__ ((aligned(JOS_CLINE)));
}  *gstate;

static uint64_t ncores;

enum { chunksize = 100 * 1024 * 1024 };
static const uint64_t nreads = 200;

static void __attribute__((noinline))
memread(void *p)
{
    // address bit A[20:16, 6] are used for DCT selection.
    // address bit A[15:7] are not used for DCT selection
    int lines = 128;
    int ret = 0;
    p += 64;
    __asm __volatile(
	    "1:\t\n"
	    "sub 	$1, %1 \t\n"
	    "je 	2f\t\n"
	    "addq 	(%0),   %%rax\t\n"
	    "addq 	8(%0),  %%rax\t\n" 
	    "addq 	16(%0), %%rax\t\n" 
	    "addq 	24(%0), %%rax\t\n" 
	    "addq 	32(%0), %%rax\t\n" 
	    "addq 	40(%0), %%rax\t\n" 
	    "addq 	48(%0), %%rax\t\n" 
	    "addq 	56(%0), %%rax\t\n"

	    "addq	$128,	%0\t\n"
	    "jmp 	1b \t\n"
	    "2:\t\n"
	    : "+r"(p), "+r"(lines), "=a"(ret));
}

void *
worker(void *arg)
{
    int c = PTR2INT(arg);
    affinity_set(lcpu_to_pcpu[c]);
    gstate->state[c].v.buf = malloc(chunksize);
    memset(gstate->state[c].v.buf, 0, chunksize);
    if (c) {
	gstate->state[c].v.ready = 1;
	while (!gstate->start) ;
    } else {
	for (int i = 1; i < ncores; i++) {
	    while (!gstate->state[i].v.ready) ;
	    gstate->state[i].v.ready = 0;
	}
	gstate->start = 1;
    }
    prof_worker_start(MAP, c);
    uint64_t start = read_tsc();
    for (int i = 0; i < nreads; i++) {
	for (int j = 0; j < chunksize / (2048 * 1024); j++)
	    memread(gstate->state[c].v.buf + 2048 * 1024 * j);
    }
    uint64_t end = read_tsc();
    prof_worker_end(MAP, c);
    gstate->state[c].v.cycles = end - start;
    gstate->state[c].v.ready = 1;
    if (!c) {
	for (int i = 1; i < ncores; i++)
	    while (!gstate->state[i].v.ready) ;
	uint64_t ncycles = 0;
	for (int i = 0; i < ncores; i++)
	    ncycles += gstate->state[i].v.cycles;
        double average_cputime_in_ms = ncycles * 1000 / (ncores * get_cpu_freq());
        double mbytes_accessed = nreads * ncores * chunksize / (1024 * 1024);
	printf("Throughput: %.1f GB/second\n", 
	    mbytes_accessed / average_cputime_in_ms);
    }
    return NULL;
}

int
main(int argc, char **argv)
{
    cpumap_init();
    affinity_set(lcpu_to_pcpu[0]);
    if (argc < 2) {
	printf("Usage: <%s> number-cores\n", argv[0]);
	exit(EXIT_FAILURE);
    }
    ncores = atoi(argv[1]);
    assert(ncores <= JOS_NCPU);
    gstate =
	mmap(NULL, sizeof(*gstate), PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS,
	     -1, 0);
    memset(gstate, 0, sizeof(*gstate));
    if (gstate == MAP_FAILED) {
	printf("mmap error: %d\n", errno);
	exit(EXIT_FAILURE);
    }
    for (int i = 1; i < ncores; i++) {
	pthread_t tid;
	pthread_create(&tid, NULL, worker, INT2PTR(i));
    }
    prof_phase_stat st;
    prof_phase_init(&st, MAP);
    worker(INT2PTR(0));
    prof_phase_end(&st);
    prof_print(ncores);
    munmap(gstate, sizeof(*gstate));
}
