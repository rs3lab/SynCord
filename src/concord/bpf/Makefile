# SPDX-License-Identifier: GPL-2.0
#
# Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# Build bpf code (kernel) out-of-tree by referencing local copies of
# bpf .h files along with headers from kernel source tree.
# Creates similar environment to that used by samples/bpf by adding
# ../include/[bpf_endian.h,bpf_helpers.h,linux/types.h]. The latter is
# used to get definitions for u64, u32 etc which are needed by other kernel
# headers.
#
# - ../include/bpf_helpers.h is a copy of tools/testing/selftest/bpf/bpf_helpers.h
# - ../include/bpf_endian.h is a copy of tools/testing/selftest/bpf/bpf_endian.h
# - ../include/linux/types.h is a copy of tools/include/linux/types.h
#
#
# Assumptions:
#
# - kernel-uek-devel package or equivalent has installed (partial) source
#   tree in /usr/src/kernels/`uname -r`
#
# - llc/clang are available and support "bpf" target; check with "llc --verison"
#

# === Need to be patched by concord ===

NAME = ${POLICY_NAME}
linuxhdrs ?= ${LINUX_SRC}

# =====================================

KERN_OBJS = ${NAME}_kern.o
COMMON_OBJS = bpf.o bpf_load.o
USER_OBJS = ${NAME}_user.o

PROG = ${NAME}
OBJS = ${COMMON_OBJS} ${USER_OBJS}

LLC ?= llc
CLANG ?= clang
INC_FLAGS = -nostdinc -isystem `$(CLANG) -print-file-name=include`
CFLAGS = -DHAVE_ATTR_TEST=0 -D__EXPORTED_HEADERS__
EXTRA_CFLAGS ?= -O2 -emit-llvm

# In case up-to-date headers are not installed locally in /usr/include,
# use source build.

# linuxhdrs ?= /usr/src/kernels/`uname -r`

LINUXINCLUDE =  -I$(linuxhdrs)/arch/x86/include/uapi \
				-I$(linuxhdrs)/arch/x86/include/generated/uapi \
				-I$(linuxhdrs)/include/generated/uapi \
				-I$(linuxhdrs)/include/uapi \
				-I$(linuxhdrs)/include \
				-I$(linuxhdrs)/arch/x86/include \

LDLIBS = -lelf

all: $(PROG) $(KERN_OBJS)

.PHONY: clean

clean:
	rm -f $(OBJS) $(KERN_OBJS) $(PROG)

%.o: %.c
	$(CC) -g -Wno-unused-variable -I../include $(LINUXINCLUDE) -c -o $@ $< $(CFLAGS)

$(PROG): $(OBJS)
	$(CC) -g -o $@ $(@)_user.o $(COMMON_OBJS) $(CFLAGS) $(LDLIBS)

$(KERN_OBJS):  %.o:%.c
	$(CLANG) $(INC_FLAGS) \
		-D__KERNEL__ -D__ASM_SYSREG_H \
		-Wno-unused-value -Wno-pointer-sign \
		-Wno-compare-distinct-pointer-types \
		-Wno-gnu-variable-sized-type-not-at-end \
		-Wno-address-of-packed-member -Wno-tautological-compare \
		-Wno-unknown-warning-option \
		-I./include $(LINUXINCLUDE) \
		$(EXTRA_CFLAGS) -c $< -o -| $(LLC) -march=bpf -filetype=obj -o $@


