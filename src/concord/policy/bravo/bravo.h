#ifndef __LINUX_LOCK_POLICY_H__
#define __LINUX_LOCK_POLICY_H__

struct __attribute__((aligned(64))) __aligned_u64_field {
	unsigned long field;
};

/*
 * User accessible mirror of in-kernel lock_policy_args.
 */
struct __lock_policy_args {
	unsigned long lock;
	unsigned long lock_ptr;
	unsigned long per_cpu_data;

	/* User-defined additional data */
	unsigned long RBias;
	unsigned long arg2;
	unsigned long arg3;
	unsigned long arg4;
	unsigned long arg5;
	unsigned long arg6;
	unsigned long arg7;
	unsigned long arg8;
};


/*
 * This is the struct to be passed to bpf lock policy
 */
struct lock_policy_args {
	void *lock;
	unsigned long lock_ptr;
	struct __aligned_u64_field *per_cpu_data;

	/* User-defined additional data */
	unsigned long *RBias;
	unsigned long *arg2;
	unsigned long *arg3;
	unsigned long *arg4;
	unsigned long *arg5;
	unsigned long *arg6;
	unsigned long *arg7;
	unsigned long *arg8;

	unsigned long tmp_reg;
};

/*
 * This is for additional data per lock instance, which
 * will be allocated and attached as shadow variable.
 */
struct per_lock_data {
	/* User-defined additional data */
	struct __aligned_u64_field per_cpu_data[${NCPU}];
	unsigned long RBias;
};

/*
 * This is for additional data per node, which will be
 * allocated in stack.
 */
struct per_node_data {
	/* User-defined additional data */
};

#endif /* __LINUX_LOCK_POLICY_H__ */
