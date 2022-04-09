// SPDX-License-Identifier: GPL-2.0

#include <stdio.h>
#include <assert.h>
#include "bpf_load.h"
#include <linux/bpf.h>
#include <string.h>

#define MAP 0

int main(int ac, char **argv)
{
	char filename[256];
	struct bpf_prog_info info = {};
	uint32_t info_len = sizeof(info);
	int err;

	snprintf(filename, sizeof(filename), "%s_kern.o", argv[0]);

	if(load_bpf_file(filename)){
		printf("ERRS");
		printf("%s", bpf_log_buf);		// inside "bpf_load.h"
		return 1;
	}
	printf("%s loaded\n", filename);

	err = bpf_obj_get_info_by_fd(prog_fd[0], &info, &info_len);
	assert(!err);
	assert(info.type == BPF_PROG_TYPE_LOCK_POLICY);
	printf("prog loaded well\n");

	err = bpf_obj_pin(prog_fd[0], "/sys/fs/bpf/${POLICY_NAME}");
	assert(!err);

#if MAP
	err = bpf_obj_pin(map_fd[0], "/sys/fs/bpf/hash_map");
	assert(!err);
#endif

	return 0;
}
