#ifndef __LINUX_LOCK_POLICY_H__
#define __LINUX_LOCK_POLICY_H__

/* Comment out below line if per-cpu data is not needed. */
// #define DEFINE_PER_CPU_DATA

struct __attribute__((aligned(64))) __aligned_u64_field {
	unsigned long field;
};

/*
 * User accessible mirror of in-kernel lock_policy_args.
 */
struct __lock_policy_args {
	/* User-defined additional data */
	unsigned long lock_ptr;
#ifdef DEFINE_PER_CPU_DATA
	/* type should match with `__aligned_u64_field->field` */
	unsigned long per_cpu_data;
#endif
};


/*
 * This is the struct to be passed to bpf lock policy
 */
struct lock_policy_args {
	/* User-defined additional data */
	unsigned long lock_ptr;
#ifdef DEFINE_PER_CPU_DATA
	struct __aligned_u64_field *per_cpu_data;
	unsigned long tmp_reg;
#endif
};

/*
 * This is for additional data per lock instance, which
 * will be allocated and attached as shadow variable.
 */
struct per_lock_data {
};

/*
 * This is for additional data per node, which will be
 * allocated in stack.
 */
struct per_node_data {
	/* User-defined additional data */
};

#endif /* __LINUX_LOCK_POLICY_H__ */
