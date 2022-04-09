// ============ Available APIs ============

// -- General --
void lock_to_acquire(struct __lock_policy_args *args);
void lock_acquired(struct __lock_policy_args *args);
void lock_to_release(struct __lock_policy_args *args);
void lock_released(struct __lock_policy_args *args);

// -- Fastpath --
void lock_to_enter_slowpath(struct __lock_policy_args *args);
bool lock_enable_fastpath(struct __lock_policy_args *args);

// -- Reordering --
bool should_reorder(struct __lock_policy_args *args);
bool skip_reorder(struct __lock_policy_args *args);

// -- Bypass --
bool lock_bypass_acquire(struct __lock_policy_args *args);
bool lock_bypass_release(struct __lock_policy_args *args);
