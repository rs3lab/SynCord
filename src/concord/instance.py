import os
import sys
import logging

from abc import ABC, abstractmethod

from util import prepdn, git_checkout

import config as CONFIG


class Instance(ABC):
    """
    Programs compiled with the host toolchain
    """

    def __init__(self, prog: str, name: str) -> None:
        # basics
        self.name = name

        # paths
        path_base = os.path.join(CONFIG.PATH_OUTS, prog, self.name)
        self.path_src = path_base
        #  self.path_src = os.path.join(path_base, 'src')
        #  self.path_obj = os.path.join(path_base, 'obj')
        #  self.path_bin = os.path.join(path_base, 'bin')
        #  self.path_log = os.path.join(path_base, 'log')

    @abstractmethod
    def _ready_impl(self, override: bool) -> None:
        raise RuntimeError('Method not implemented')

    def ready(self, override: bool = False) -> None:
        # prepare the base directory
        if os.path.exists(self.path_src) and not override:
            logging.info('Path {} existed, do nothing'.format(self.path_src))
            return

        prepdn(self.path_src, override)

        try:
            # tool-specific routine
            self._ready_impl(override)

            # finish
            logging.info('[Done] Ready')

        except Exception as e:
            logging.error('[Fail] Ready')
            print(e)
            sys.exit()

    @abstractmethod
    def _setup_impl(self, override: bool) -> None:
        raise RuntimeError('Method not implemented')

    def setup(self, override: bool = False) -> None:

        try:
            # tool-specific routine
            self._setup_impl(override)
            logging.info('[Done] Setup')

        except Exception as e:
            logging.error('[Fail] Setup')
            print(e)
            sys.exit()


    @abstractmethod
    def _build_impl(self, override: bool) -> None:
        raise RuntimeError('Method not implemented')

    def build(self, override: bool = False) -> None:

        try:
            # tool-specific routine
            self._build_impl(override)
            logging.info('[Done] Build')

        except Exception as e:
            logging.error('[Fail] Build')
            print(e)
            sys.exit()

    @abstractmethod
    def _check_impl(self) -> bool:
        raise RuntimeError('Method not implemented')

    def check(self) -> None:

        try:
            # tool-specific routine
            self._check_impl()
            logging.info('[Done] Check')

        except Exception as e:
            logging.error('[Fail] Check')
            print(e)
            sys.exit()


