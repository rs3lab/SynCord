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

static uint64_t alloc_core;
static uint64_t access_core;

enum { chunksize = 100 * 1024 * 1024 };
static const uint64_t nreads = 200;

static void __attribute__((noinline))
memread(void *p, uint32_t size)
{
    int lines = size / 64;
    uint64_t ret = 0;
    __asm __volatile(
	    "1:\t\n"
	    "sub 	$1, %1 \t\n"
	    "je 	2f\t\n"
#if 0
	    "addq 	(%0),   %%rax\t\n"
	    "addq 	64(%0),   %%rax\t\n"
	    "addq 	128(%0),   %%rax\t\n"
	    "addq 	192(%0),   %%rax\t\n"
	    "addq 	256(%0),   %%rax\t\n"
	    "addq 	320(%0),   %%rax\t\n"
	    "addq 	384(%0),   %%rax\t\n"
	    "addq 	448(%0),   %%rax\t\n"
#endif
#if 0
	    "addq 	(%0),   %%rax\t\n"
	    "addq 	8(%0),  %%rax\t\n" 
	    "addq 	16(%0), %%rax\t\n" 
	    "addq 	24(%0), %%rax\t\n" 
	    "addq 	32(%0), %%rax\t\n" 
	    "addq 	40(%0), %%rax\t\n" 
	    "addq 	48(%0), %%rax\t\n" 
	    "addq 	56(%0), %%rax\t\n"
#endif
#if 1
	    "movq 	(%0),  %%rax\t\n" 
	    "movq 	8(%0),  %%rax\t\n" 
	    "movq 	16(%0), %%rax\t\n" 
	    "movq 	24(%0), %%rax\t\n" 
	    "movq 	32(%0), %%rax\t\n" 
	    "movq 	40(%0), %%rax\t\n" 
	    "movq 	48(%0), %%rax\t\n" 
	    "movq 	56(%0), %%rax\t\n"
#endif
	    "addq	$64,	%0\t\n"
	    "jmp 	1b \t\n"
	    "2:\t\n"
	    : "+r"(p), "+r"(lines), "=a"(ret));
}

void *
alloc_worker(void *arg)
{
    int c = PTR2INT(arg);
    affinity_set(lcpu_to_pcpu[c]);
    gstate->state[c].v.buf = malloc(chunksize);
    memset(gstate->state[c].v.buf, 0, chunksize);
    gstate->state[c].v.ready = 1;

    prof_worker_start(MAP, c);
    while (!gstate->state[access_core].v.ready);
    prof_worker_end(MAP, c);
    return NULL;
}


void *
access_worker(void *arg)
{
    int c = PTR2INT(arg);
    affinity_set(lcpu_to_pcpu[c]);
    while (!gstate->state[alloc_core].v.ready) ;

    uint64_t start = read_tsc();
    for (int i = 0; i < nreads; i++) {
	if (i == 0)
	    prof_worker_start(MAP, c);
	memread(gstate->state[alloc_core].v.buf, chunksize);
    }
    uint64_t end = read_tsc();
    prof_worker_end(MAP, c);
    uint64_t ncycles = end - start;

    gstate->state[access_core].v.ready = 1;
    sleep(1);
    double average_cputime_in_ms = ncycles * 1000 / get_cpu_freq();
    double mbytes_accessed = nreads * chunksize / (1024 * 1024);
    printf("Throughput: %.1f GB/second\n", 
	    mbytes_accessed / average_cputime_in_ms);
    return NULL;
}

int
main(int argc, char **argv)
{
    cpumap_init();
    access_core = 0;
    affinity_set(lcpu_to_pcpu[access_core]);
    if (argc < 2) {
	printf("Usage: <%s> [alloc-core]\n", argv[0]);
	exit(EXIT_FAILURE);
    }
    alloc_core = atoi(argv[1]);
    gstate =
	mmap(NULL, sizeof(*gstate), PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS,
	     -1, 0);
    memset(gstate, 0, sizeof(*gstate));
    if (gstate == MAP_FAILED) {
	printf("mmap error: %d\n", errno);
	exit(EXIT_FAILURE);
    }
    for (int i = alloc_core; i <= alloc_core; i++) {
	pthread_t tid;
	pthread_create(&tid, NULL, alloc_worker, INT2PTR(i));
    }
    prof_phase_stat st;
    prof_phase_init(&st, MAP);
    access_worker(INT2PTR(access_core));
    prof_phase_end(&st);
    prof_print(alloc_core + 1);
    munmap(gstate, sizeof(*gstate));
}
