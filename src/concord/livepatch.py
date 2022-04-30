import os
import sys
import subprocess

from instance import Instance
from util import cd, prepdn, execute, copy_all_files, inplace_replace
from enum import Enum

import logging
import config as CONFIG

class PATCH_GEN(Instance):

    def __init__(self,
            name: str,
            linux_src: str,
            pname: str,
            aux_data: str,
            livepatch) -> None:
        super(PATCH_GEN, self).__init__('LivePatchGen', name)

        self.linux_src = linux_src
        self.policy_name = pname
        self.aux_data = aux_data
        self.livepatch = livepatch


    def _setup_impl(self, override: bool) -> None:
        # Create obj directory
        logging.info('[Start] PATCH Setup: Patch kernel to expose CONCORD APIs...')

        # logging.debug("Patch kernel with :" + self.api_patch)
        with cd(self.linux_src):
            # cmd = ["patch", "-p3"]
            # with open(self.api_patch, 'r') as stdin:
                # execute(cmd, stdin=stdin)

            ncpu = os.cpu_count()
            cmd = ["cp", self.aux_data, os.path.join(self.linux_src, "include/linux/lock_policy.h")]
            execute(cmd)
            inplace_replace(os.path.join(self.linux_src, "include/linux/lock_policy.h"), "${NCPU}",
                    str(ncpu))


    def _ready_impl(self, override: bool) -> None:
        # Create src, log directory
        logging.info('[Start] PATCH Ready: Create patch file for kpatch...')

        if self.livepatch is None:
            # Copy skeleton code to create patch
            copy_all_files(CONFIG.PATCH_PATH, self.path_src, True)

            # ===== Patch file =====
            # pre_patch_callback
            prepatch = os.path.join(self.path_src, CONFIG.KPATCH_PRE_CALL)
            inplace_replace(prepatch, "${API_NAME}", "custom_cmp_func")  # TODO
            inplace_replace(prepatch, "${POLICY_NAME}", self.policy_name)

            # rwsem API: Nothing to change

            # Applying granularity
            # TODO: Need more design..
            # Now, just replace down_write -> bpf_down_write

            # Merge three patches into one.
            with cd(self.path_src):
                logging.debug('merge patches for lock type + applying granularity')
                cmd = ["combinediff", "rwsem_custom_cmp_func.patch", "single_lock.patch"]
                with open("temp.patch", 'w') as stdout:
                    execute(cmd, stdout=stdout)

                logging.debug('merge with pre patch callback function')
                cmd = ["combinediff", "temp.patch", CONFIG.KPATCH_PRE_CALL]
                with open(CONFIG.KPATCH_RESULT, 'w') as stdout:
                    execute(cmd, stdout=stdout)

        else:
            # User provide own patch file. No need to create one.
            with cd(self.path_src):
                cmd = ["cp", self.livepatch, CONFIG.KPATCH_RESULT]
                execute(cmd)


    def _build_impl(self, override: bool) -> None:
        # Create bin directory
        logging.info('[Start] Build: compile livepatch module...')

        # Build Kernel
        with cd(self.linux_src):
            cmd = ["make", "-j", str(CONFIG.NCPU)]
            execute(cmd)

        with cd(self.path_src):
            kpatch = CONFIG.KPATCH_PATH + "/kpatch-build/kpatch-build"
            cmd = [kpatch, \
                    "-j", str(CONFIG.NCPU), \
                    "-t", "vmlinux", \
                    "-s", self.linux_src, \
                    "--vmlinux", self.linux_src + "/vmlinux", \
                    CONFIG.KPATCH_RESULT]
            logging.debug(cmd)

            logging.warning("This might take time! kpatch builds kernel twice")
            execute(cmd)


    def _check_impl(self) -> bool:
        # Do checking.. and get compiled module
        logging.info('[Start] Check: Checking livepatch ...')

        mod_path = os.path.abspath(os.path.join(self.path_src, CONFIG.KPATCH_MODULE))

        try:
            assert os.path.exists(mod_path)
            logging.debug("Found module: " + mod_path)
            self.module = mod_path

        except AssertionError as e:
            logging.error("Compiled module not found")
            self.module = None
