#include "perf.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

static int cur_phase = 0;
static char cmd[512];
static int started = 0;

enum { all_phases_in_one = 1 };
//#define event "-e r0d8"
#define event ""	

void perf_start(task_type_t phase)
{
    cur_phase = phase;
    if (all_phases_in_one && started)
	return;
    started = 1;
    // recording self does not work with multiple cores
    //sprintf(cmd, "sudo ./tools/perf record "event" -g -p %d &", getpid());
    sprintf(cmd, "sudo ./tools/perf record "event" -g -a &");
    fprintf(stderr, "Command is %s\n", cmd);
    system(cmd);
}

void perf_end()
{
    if (all_phases_in_one && cur_phase != MERGE)
	return;
    system("sudo killall -s 2 perf");
    if (all_phases_in_one)
        return;
    sleep(1);
    sprintf(cmd, "sudo mkdir -p perf; sudo mv perf.data perf/%d.data", cur_phase);
    system(cmd);
}

