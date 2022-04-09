import os
import sys
import subprocess

from instance import Instance
from util import cd, prepdn, execute, copy_all_files, inplace_replace

import logging
import config as CONFIG
import re

ret_type = ['void', 'bool', 'int']
arg_type = ['struct __lock_policy_args*']

class CONCORD_API:

    def __init__(self,
            ret: str,
            func_name: str,
            num_arg: int) -> None:
        try:
            assert ret in ret_type
            assert len(func_name) > 0

        except AssertionError as e:
            logging.error("Wrong API usage")
            print(e)
            sys.exit()

        self.ret = ret
        self.func_name = func_name
        self.num_arg = num_arg
        self.args = []

    def add_arg(self, arg: str) -> None:

        if len(self.args) >= self.num_arg:
            logging.error("Wrong API usage: too many args")
            sys.exit()
        else:
            try:
                assert arg in arg_type
            except AssertionError as e:
                logging.error("Wrong API usage: args not defined")
                sys.exit()

            self.args.append(arg)

    def __repr__(self):
        retstr = self.ret + " " + self.func_name + "("
        for arg in self.args:
            retstr += arg + ","
        retstr = retstr.rstrip(", ")

        retstr += ")"
        return retstr

    def __str__(self):
        retstr = self.ret + " " + self.func_name + "("
        for arg in self.args:
            retstr += arg + ", "
        retstr = retstr.rstrip(", ")

        retstr += ")"
        return retstr

class EBPF_GEN(Instance):

    def __init__(self, name: str, linux_src: str, policy_file: str, aux_data: str) -> None:
        super(EBPF_GEN, self).__init__('eBPFGen', name)
        self.linux_src = linux_src
        self.policy_file = policy_file
        self.aux_data= aux_data
        self.list_API = {}

    def get_section(self) -> str:
        # Get section specified in pfile
        try:
            with open(self.policy_file) as f:
                name = re.findall('SEC\(\"(.*?)\"\)', f.read())
                return name
        except Exception as e:
            logging.error("Section not found")
            print(e)
            sys.exit()

    def _ready_impl(self, override: bool) -> None:
        # Create src, log directory
        logging.info('[Start] EBPF Ready: Prepare eBPF source code...')

        # Copy skeleton code to compile eBPF program
        copy_all_files(CONFIG.BPF_PATH, self.path_src, True)
        cmd = ["cp", self.aux_data, os.path.join(self.path_src, "include/concord.h")]
        execute(cmd)

        # ===== Patch file =====
        # Makefile
        makefile = os.path.join(self.path_src, 'Makefile')
        inplace_replace(makefile, "${POLICY_NAME}", self.name)
        inplace_replace(makefile, "${LINUX_SRC}", self.linux_src)

        # Policy file name (kern)
        bpf_kern_init = os.path.join(self.path_src, CONFIG.BPF_SKELETON_KERN)

        # Include user's policy in the eBPF src
        with open(self.policy_file) as f:
            contents = f.read()
            inplace_replace(bpf_kern_init, "${API_CONTENTS}", contents)

        bpf_kern = os.path.join(self.path_src, self.name+"_kern.c")
        os.rename(bpf_kern_init, bpf_kern)

        # Policy file name (user)
        bpf_user_init = os.path.join(self.path_src, CONFIG.BPF_SKELETON_USER)
        inplace_replace(bpf_user_init, "${POLICY_NAME}", self.name)

        bpf_user = os.path.join(self.path_src, self.name+"_user.c")
        os.rename(bpf_user_init, bpf_user)

        # Header file
        bpf_header_init = os.path.join(self.path_src, "include/concord.h")
        ncpu = os.cpu_count()
        logging.info('Number of CPUs: ' + str(ncpu))
        inplace_replace(bpf_header_init, "${NCPU}", str(ncpu))




    def _setup_impl(self, override: bool) -> None:
        # Create obj directory
        #  logging.info('setup for generating eBPF')
        # Do nothing
        return


    def _build_impl(self, override: bool) -> None:
        # Create bin directory
        # Make
        logging.info('[Start] EBPF Build: compile eBPF policy...')
        with cd(self.path_src):
            cmd = ["make"]
            execute(cmd)


    def read_API_list(self) -> None:
        # Read APIs from the list_APIs.h and construct a dict.
        p = re.compile("""
            ^
            \s*
            (void|bool|int)     # ret
            \s+
            (\w+)           # func_name
            \s*
            \(              # (
            ([^)]*)         # args
            \)              # )
            \s*
            ;
            """, re.MULTILINE | re.VERBOSE)

        with open(CONFIG.API_PATH) as f:
            lines = f.read()
            funcs = p.findall(lines)

            for func in funcs:
                args = re.split(',\s*', func[2].strip())
                api_func = CONCORD_API(func[0], func[1], len(args))

                for arg in args:
                    name_index = arg.rfind(' ')
                    arg_type = arg[:name_index]
                    if arg[name_index+1] == '*':
                        arg_type += '*'

                    api_func.add_arg(arg_type)

                self.list_API[func[1]] = api_func

    def print_API(self) -> None:
        logging.info("=== API List ===")
        for item in self.list_API.keys():
            print("\t>", self.list_API[item])


    def _check_impl(self) -> bool:
        # Do checking.. and log
        # Check API matching
        logging.info('[Start] EBPF Check: Checking APIs...')

        self.read_API_list()
        self.print_API()

        # Section check
        sections = self.get_section()
        for section in sections:
            logging.info("SEC = \""+ section + "\"")
            try:
                # TODO: Need to revisit if want to support multiple maps..
                if section.startswith("maps"):
                    bpf_user = os.path.join(self.path_src, self.name+"_user.c")
                    inplace_replace(bpf_user, "#define MAP 0", "#define MAP 1")
                else:
                    assert section.startswith("lock_")
            except AssertionError as e:
                logging.error("Bad Section")
                sys.exit()

        # Check with API list
        # TODO: Parse user's function and get the name of api

