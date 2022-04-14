import os
import multiprocessing

# Linux path
PATH = os.path.abspath(os.path.join(__file__, '..'))
BPF_PATH = os.path.join(PATH, "bpf")
KPATCH_PATH = os.path.join(PATH, "..", "kpatch")
PATCH_PATH = os.path.join(PATH, "patch")
PATH_OUTS = os.path.join(PATH, "output")

# Default file name for eBPF programs (./bpf/)
BPF_SKELETON_KERN = 'skeleton_kern.c'
BPF_SKELETON_USER = 'skeleton_user.c'

# Default file name for kpatch patches (./patch/)
# On-going implementation to automate the patch file creation
KPATCH_PRE_CALL = 'pre_patch_callback.patch'
KPATCH_RESULT = 'concord.patch'
KPATCH_MODULE = 'livepatch-concord.ko'

# Default policy
POLICY_PATH = os.path.join(PATH, "policy")
POLICY_AUX_DATA = os.path.join(POLICY_PATH, "lock_policy.h")
POLICY_PIN = "/sys/fs/bpf/"

# List of APIs
API_PATH = os.path.join(PATH, "list_APIs.h")

# misc
NCPU = multiprocessing.cpu_count()
