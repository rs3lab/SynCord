#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <pthread.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include "bench.h"
#include "lib/profile.h"
#include "lib/cpumap.h"
#include <sys/resource.h>
#include <sys/time.h>

static struct {
    volatile int start;
    union {
	struct {
	    volatile int ready;
	    volatile uint64_t cycles;
	} v;
	char __pad[JOS_CLINE];
    } state[JOS_NCPU] __attribute__ ((aligned(JOS_CLINE)));
} gstate;

static int ncores;
static uint64_t nbytes;
static uint64_t nchks;

void *
worker(void *arg)
{
    int c = PTR2INT(arg);
    affinity_set(lcpu_to_pcpu[c]);
    char **addrs = malloc(nchks * sizeof(char *));
    memset(addrs, 0, nchks * sizeof(char *));
//#define INC_MMAP // including the time of memory map
#ifndef INC_MMAP
    for (int i = 0; i < nchks; i++) {
	addrs[i] = (char *)malloc(nbytes);
    }
#endif
    struct rusage rs;
    getrusage(RUSAGE_SELF, &rs);
    if (c) {
	gstate.state[c].v.ready = 1;
	while (!gstate.start) ;
    } else {
	for (int i = 1; i < ncores; i++) {
	    while (!gstate.state[i].v.ready) ;
	    gstate.state[i].v.ready = 0;
	}
	gstate.start = 1;
    }
    prof_worker_start(MAP, c);
    uint64_t start = read_tsc();
#ifdef INC_MMAP
    for (int i = 0; i < nchks; i++) {
	addrs[i] = (char *)malloc(nbytes);
    }
#endif
    for (int i = 0; i < nchks; i++) {
	for (char *p = addrs[i]; p < addrs[i] + nbytes; p += 4096)
	    p[0] = 0;
    }
    uint64_t end = read_tsc();
    prof_worker_end(MAP, c);
    gstate.state[c].v.cycles = end - start;
    gstate.state[c].v.ready = 1;
    if (!c) {
	for (int i = 1; i < ncores; i++)
	    while (!gstate.state[i].v.ready) ;
	uint64_t ncycles = 0;
	for (int i = 0; i < ncores; i++)
	    ncycles += gstate.state[i].v.cycles;
	struct rusage re;
	getrusage(RUSAGE_SELF, &re);
        uint64_t nminflts = re.ru_minflt - rs.ru_minflt;
        uint64_t nmajflts = re.ru_majflt - rs.ru_majflt;
        assert(nmajflts == 0);
	fprintf(stderr, "# pagefaults: %ld, cycles per page fault: %ld\n", 
	    nminflts, ncycles / nminflts);
    }
    return NULL;
}

int
main(int argc, char **argv)
{
    cpumap_init();
    assert(affinity_set(lcpu_to_pcpu[0]) == 0);
    if (argc < 4) {
	fprintf(stderr, "Usage: <%s> number-cores chkkb nchks\n", argv[0]);
	exit(EXIT_FAILURE);
    }
    ncores = atoi(argv[1]);
    nbytes = atoi(argv[2]) * 1024;
    nchks = atoi(argv[3]);
    assert(ncores <= JOS_NCPU);
    for (int i = 1; i < ncores; i++) {
	pthread_t tid;
	pthread_create(&tid, NULL, worker, INT2PTR(i));
    }
    prof_phase_stat st;
    prof_phase_init(&st, MAP);
    uint64_t start = read_tsc();
    worker(INT2PTR(0));
    uint64_t end = read_tsc();
    prof_phase_end(&st);
    prof_print(ncores);
    printf("Real time %ld ms\n", (end - start) / 2000000);
}
