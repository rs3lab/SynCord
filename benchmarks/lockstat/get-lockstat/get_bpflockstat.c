// SPDX-License-Identifier: GPL-2.0-only
/* Copyright (c) 2016 Facebook
 */
/**  */
#include <stdio.h>
#include <linux/bpf.h>
#include "bpf_load.h"

struct time_stat{
	unsigned long min;
	unsigned long max;
	unsigned long total;
};

struct data_t{
	/* User-defined additional data */
	unsigned long prev_cpu;

	/* lock_to_enter_slow_path */
	unsigned long contentions;
	unsigned long con_bounces;
	struct time_stat waittime;

	/* lock_acquired */
	unsigned long acquisitions;
	unsigned long acq_bounces;
	struct time_stat holdtime;

};

static void print_stack(unsigned long *key, struct data_t *data)
{
	printf("%16p %15lu %15lu %15lu %15lu %10lu %10lu %10lu %10lu %10lu %10lu\n",
			key,
			data->contentions, data->con_bounces, data->acquisitions, data->acq_bounces,
			data->waittime.min, data->waittime.max, data->waittime.total,
			data->holdtime.min, data->holdtime.max, data->holdtime.total);
}

static void print_stacks(int fd)
{
	unsigned long key, next_key;
	struct data_t data;

	printf("==================================================================================================================================================\n");
	printf("%16s ", "lock addr");

	printf("%15s ", "contentions");
	printf("%15s ", "con-bounces");
	printf("%15s ", "acquisition");
	printf("%15s ", "acq-bounces");

	printf("%10s ", "wait-min");
	printf("%10s ", "wait-max");
	printf("%10s ", "wait-tot");
	printf("%10s ", "hold-min");
	printf("%10s ", "hold-max");
	printf("%10s ", "hold-tot");

	printf("\n==================================================================================================================================================\n");

	while (bpf_map_get_next_key(fd, &key, &next_key) == 0) {
		int res = bpf_map_lookup_elem(fd, &next_key, &data);
		if(res < 0){
			printf("NOT FOUND\n");
		}
		print_stack(&next_key, &data);

		key = next_key;
	}
}

int main(int argc, char **argv)
{
	int fd = bpf_obj_get("/sys/fs/bpf/hash_map");

	if(fd <0){
		printf("bpf_obj_get error %d\n", fd);
		return -1;
	}

	print_stacks(fd);

	return 0;
}
