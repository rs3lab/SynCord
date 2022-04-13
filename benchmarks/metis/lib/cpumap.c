#include "lib/cpumap.h"
#include "lib/bench.h"
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>
#include <string.h>

int lcpu_to_pcpu[JOS_NCPU];

void
cpumap_init()
{
    char *cpuseq;
    if (!(cpuseq = getenv("CPUSEQ"))) {
	// default cpumap provided by the system
	for (int i = 0; i < JOS_NCPU; i++)
	    lcpu_to_pcpu[i] = i;
	return;
    }

    for (int i = 0; i < JOS_NCPU; i++) {
	if (!*cpuseq) {
	    lcpu_to_pcpu[i] = -1;
	    continue;
	}
	char *next;
	errno = 0;
	lcpu_to_pcpu[i] = strtol(cpuseq, &next, 10);
	assert(errno == 0);
	assert(next != cpuseq);
	cpuseq = next;
	if (*next == ',' || *next == ' ')
	    cpuseq++;
	else
	    assert(!*next);
    }
}
