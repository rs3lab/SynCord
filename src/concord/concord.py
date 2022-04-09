#!/usr/bin/env python3

from typing import List, Optional

import os
import sys
import logging
import re

from argparse import ArgumentParser

from util import cd, envpaths, execute2, enable_coloring_in_logging, find_all_files

import config as CONFIG

import bpfgen
import livepatch

class LockGen(object):

    def __init__(self,
                 linux_src: str,
                 policy_dir: str,
                 livepatch: str,
                 bpfonly: int
                 ) -> None:
        self.linux_src = linux_src
        self.policy_dir = policy_dir
        self.livepatch = livepatch
        self.bpfonly = bpfonly

        # Default aux data
        self.aux_data = CONFIG.POLICY_AUX_DATA

        self.patched_lock_module = None
        self.lock_ebpf = None

    def get_name(self, path: str) -> str:
        # Get name of the file
        try:
            filename = os.path.basename(path)
            return os.path.splitext(filename)[0]
        except Exception as e:
            logging.error("Name not found")
            print(e)
            sys.exit()

    def _setup(self, debug: Optional[str] = None) -> None:
        # setup logging
       prepdn(self.path_log, override = True)

    def _check_and_gen_ebpf(self) -> None:

        policy_files = find_all_files(self.policy_dir, re.compile('(.*)\.pfile'))
        aux_data = find_all_files(self.policy_dir, re.compile('(.*)\.h'))

        if aux_data:
            self.aux_data = aux_data[0]

        # TODO: Merge policy file into one
        for policy_file in policy_files:
            policy_name = self.get_name(policy_file)
            ebpf_gen = bpfgen.EBPF_GEN(policy_name,\
                    self.linux_src,\
                    policy_file, \
                    self.aux_data)

            # Create `./output/eBPFGen/<name>/src` and prepare src codes to compile
            # eBPF program
            ebpf_gen.ready(True)

            # Get user's policy and check whether it matches with exposed API
            ebpf_gen.check()

            # Compile eBPF
            ebpf_gen.build()

        return ebpf_gen


    def _verify(self) -> str:
        return self.lock_ebpf

    def _patch_kernel(self) -> None:
        lock_name = self.get_name(self.livepatch)
        livepatch_gen = livepatch.PATCH_GEN(lock_name,\
                self.linux_src,\
                self.lock_ebpf.name, \
                self.aux_data, \
                self.livepatch)

        # Patch Kernel to expose APIs
        # (under patch/expose_api.patch)
        livepatch_gen.setup()

        # Create patch file for kpatch
        livepatch_gen.ready(True)

        # Create livepatch module
        # Use kpatch
        livepatch_gen.build()

        # Do checking
        livepatch_gen.check()

        #  self.patched_lock_module = livepatch_gen.module
        return livepatch_gen

    def generate_lock_code(self) -> int:
        self.lock_ebpf = self._check_and_gen_ebpf()

        if self.lock_ebpf is None:
            return -2

        logging.info(self.bpfonly)

        if self.bpfonly == 1:
            return 0

        # Now generate the kernel module
        self.patched_lock_module = self._patch_kernel().module

        if self.patched_lock_module is None:
            return -1

        return 0


def main(argv: List[str]) -> int:
    # setup argument parser
    parser = ArgumentParser()

    # logging configs
    parser.add_argument(
        '-v', '--verbose', action='count', default=1,
        help='verbose level'
    )

    # only ebpf
    parser.add_argument(
        '-e', '--bpfonly', action='count', default=0,
        help='compile only eBPF'
    )

    # linux repo
    parser.add_argument(
        '--linux_src', required=True,
        type=os.path.abspath,
        help='linux source for generating patch'
    )

    # user policy directory
    parser.add_argument(
        '--policy', required=True,
        type=os.path.abspath,
        help='a directory contains policy and auxiliary data'
    )

    # user's patch file (optional)
    parser.add_argument(
        '--livepatch',
        type=os.path.abspath,
        help='livepatch file'
    )

    # parse
    args = parser.parse_args(argv)

    # prepare logs
    LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
    LOG_LEVEL = \
            logging.WARNING if args.verbose == 0 else \
            logging.INFO if args.verbose == 1 else \
            logging.DEBUG

    enable_coloring_in_logging()

    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

    lockgen = LockGen(
        linux_src=args.linux_src,
        policy_dir=args.policy,
        livepatch=args.livepatch,
        bpfonly=args.bpfonly
    )

    ret = lockgen.generate_lock_code()

    if ret != 1:
        return ret

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
