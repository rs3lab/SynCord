// SPDX-License-Identifier: GPL-2.0
// Do not directly use this file!
// This file is a template for SynCord policy progarm.

#include <stdio.h>
#include <assert.h>
#include "bpf_load.h"
#include <linux/bpf.h>
#include <string.h>

#define MAP 0
#define MAX_NAME_LEN 256
#define MAX_NUM_POLICY 5

int main(int ac, char **argv)
{
	char filename[MAX_NAME_LEN];
	char *policy_name[MAX_NUM_POLICY] = {${POLICY_LIST}};

	struct bpf_prog_info info[MAX_NUM_POLICY] = {};
	uint32_t info_len = sizeof(info);
	int err, i;

	snprintf(filename, sizeof(filename), "%s_kern.o", argv[0]);

	if(load_bpf_file(filename)){
		printf("ERRS");
		printf("%s", bpf_log_buf);		// inside "bpf_load.h"
		return 1;
	}
	printf("%s loaded\n", filename);

	for(i = 0; i <${NUM_POLICY}; i++){
		err = bpf_obj_get_info_by_fd(prog_fd[i], &info[i], &info_len);
		assert(!err);
		assert(info[i].type == BPF_PROG_TYPE_LOCK_POLICY);

		err = bpf_obj_pin(prog_fd[i], policy_name[i]);
		assert(!err);

		printf("%s loaded and pinned\n", policy_name[i]);
	}

#if MAP
	err = bpf_obj_pin(map_fd[0], "/sys/fs/bpf/hash_map");
	assert(!err);
	printf("hashmap pinned\n");
#endif

	return 0;
}
