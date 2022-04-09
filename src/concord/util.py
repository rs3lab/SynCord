from typing import Callable, IO, Iterator, List, Optional, Pattern, TypeVar

import os
import sys
import stat
import shutil
import logging
import tarfile
import tempfile
import subprocess

from git import Repo  # type: ignore
from contextlib import contextmanager
from multiprocessing import Pool


# with statements
@contextmanager
def cd(pn: str) -> Iterator[None]:
    """
    change directory
    """

    cur = os.getcwd()
    os.chdir(os.path.expanduser(pn))
    try:
        yield
    finally:
        os.chdir(cur)


@contextmanager
def environ(key: str,
            value: Optional[str],
            concat: Optional[str] = None,
            prepend: bool = True) -> Iterator[None]:
    """
    Temporarily change the environment variable.
    If value is None, the environment variable is removed.
    If prepend is True, the environment variable is prepended.
    """

    def _set_env(key: str, value: Optional[str]) -> None:
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    old_value = os.environ.get(key, None)

    if value is None or concat is None or old_value is None:
        new_value = value
    elif prepend:
        new_value = value + concat + old_value
    else:
        new_value = old_value + concat + value

    _set_env(key, new_value)

    try:
        yield
    finally:
        _set_env(key, old_value)


@contextmanager
def envpaths(*path: str) -> Iterator[None]:
    """
    Prepend the PATH variable
    """

    with environ('PATH', value=':'.join(path), concat=':', prepend=True):
        yield


@contextmanager
def envldpaths(*path: str) -> Iterator[None]:
    """
    Prepend the LD_LIBRARY_PATH variable
    """

    with environ(
            'LD_LIBRARY_PATH', value=':'.join(path), concat=':', prepend=True
    ):
        yield


@contextmanager
def envpreload(path: str) -> Iterator[None]:
    """
    Assign the LD_PRELOAD variable
    """

    with environ(
            'LD_PRELOAD', value=path
    ):
        yield


@contextmanager
def nop() -> Iterator[None]:
    """
    A dummy context manager, used in conditional with
    """

    yield None


# command execution
def execute(cmd: List[str],
            stdout: IO = sys.stdout,
            stderr: IO = sys.stderr,
            timeout: Optional[int] = None,
            stdin: IO = sys.stdin) -> None:
    """
    Execute command and return whether the command finished successfully.
    If stdout/stderr is not None, use the file object specified.
    If tee is True, also print the stdout/stderr to console.
    """

    with subprocess.Popen(
            cmd,
            bufsize=1, universal_newlines=True,
            stdout=stdout, stderr=stderr, stdin=stdin,
    ) as p:
        while True:
            try:
                rc = p.wait(timeout=timeout)
                if rc != 0:
                    raise RuntimeError(
                        'Failed to execute {}: exit code {}'.format(
                            ' '.join(cmd), rc
                        )
                    )
                return
            except subprocess.TimeoutExpired:
                p.kill()
                raise RuntimeError(
                    'Failed to execute {}: timed out'.format(' '.join(cmd))
                )


def execute1(cmd: List[str],
             timeout: Optional[int] = None) -> None:
    """
    Same as execute, but direct all outputs to /dev/null
    """

    with open(os.devnull, 'w') as fout:
        with open(os.devnull, 'w') as ferr:
            execute(cmd, fout, ferr, timeout)


def execute2(cmd: List[str],
             path_log: str,
             timeout: Optional[int] = None) -> None:
    """
    Same as execute, but allows specification of path_log.
    """

    path_out = path_log + '.out'
    path_err = path_log + '.err'
    with open(path_out, 'w') as stdout:
        with open(path_err, 'w') as stderr:
            execute(cmd, stdout, stderr, timeout)


def execute3(cmd: List[str],
             pout: str,
             perr: str,
             timeout: Optional[int] = None) -> None:
    """
    Same as execute, but allows specification of both pout and perr.
    """

    with open(pout, 'w') as stdout:
        with open(perr, 'w') as stderr:
            execute(cmd, stdout, stderr, timeout)


# file operations
def inplace_replace(filepath: str, needle: str, replace: str) -> None:
    """
    Replace every needle in the file
    """

    with tempfile.NamedTemporaryFile('w') as tmp:
        with open(filepath) as f:
            for line in f:
                newline = line.replace(needle, replace)
                tmp.write(newline)

        tmp.flush()
        shutil.copyfile(tmp.name, filepath)

def copy_all_files(src_path: str, dst_path: str, override: bool = False) -> None:
    """
    Copy all files in src_path to dst_path.
    If override is True, remove the old directory and create a new one.
    """

    if override and os.path.exists(dst_path):
        shutil.rmtree(dst_path)

    shutil.copytree(src_path, dst_path)


# filesystem operations
def prepdn(path: str, override: bool = False) -> None:
    """
    Create a directory at path.
    If override is True, remove the old directory and create a new one.
    """

    if os.path.exists(path) and override:
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def prepfn(path: str, override: bool = False) -> None:
    """
    Prepare the parent directories so we can write a file at path.
    If override is True, remove the old file at path.
    """

    if os.path.exists(path) and override:
        os.unlink(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)


def find_all_files(base: str, regex: Optional[Pattern] = None) -> List[str]:
    """
    Find all files under the base directory
    """

    result = []  # type: List[str]
    for dirpath, _, files in os.walk(base):
        for name in files:
            if regex is None or regex.match(name) is not None:
                result.append(os.path.join(dirpath, name))
    return result


def enable_exec(path: str) -> None:
    """
    Allow the file to be executed
    """
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)


# multi-processing
T = TypeVar('T')
R = TypeVar('R')


def parralize(
        func: Callable[[T], R],
        args: List[T],
        ncpu: Optional[int] = None) -> List[R]:
    with Pool(ncpu) as pool:
        try:
            return pool.map(func, args)
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
            raise RuntimeError('Interrupted')


# git utils
def git_checkout(repo: str, refs: str, path: str) -> None:
    """
    Checkout repo with refs into directory in path
    """

    # construct repo
    mod = Repo(repo)

    # check remotes
    assert len(mod.remotes) == 1
    assert mod.remotes[0].name == 'origin'
    remote = mod.remotes.origin

    # check dirty
    assert not mod.is_dirty(untracked_files=True)

    # test whether refs is a remote branch
    name = '{}/{}'.format(remote.name, refs)
    for item in remote.refs:
        if item.name == name:
            refs = name
            break

    # rev-parse to get the commit hash
    commit = mod.rev_parse(refs).hexsha

    with tempfile.TemporaryFile() as f:
        try:
            mod.archive(f, treeish=commit, format='tar')
        except Exception as ex:
            raise RuntimeError(
                'Failed to archive refs \'{}\' on repo {}: {}'.format(
                    commit, repo, ex
                )
            )

        f.flush()
        f.seek(0)

        with tarfile.open(fileobj=f, mode='r') as tarf:
            tarf.extractall(path)


def git_patch(repo: str, patch: str) -> None:
    """
    Apply a git-formatted patch to a directory
    """

    with cd(repo):
        execute(['patch', '-p1', '-i', patch])


# logging utils
@contextmanager
def multiplex_logging(path: str, mode: str = 'w') -> Iterator[None]:
    handler = logging.FileHandler(path, mode=mode)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)
    try:
        yield
    finally:
        logging.getLogger().removeHandler(handler)
        handler.close()


def enable_coloring_in_logging() -> None:
    logging.addLevelName(
        logging.CRITICAL,
        '\033[1;31m%s\033[1;0m' % logging.getLevelName(logging.CRITICAL),
    )
    logging.addLevelName(
        logging.ERROR,
        '\033[1;31m%s\033[1;0m' % logging.getLevelName(logging.ERROR),
    )
    logging.addLevelName(
        logging.WARNING,
        '\033[1;33m%s\033[1;0m' % logging.getLevelName(logging.WARNING),
    )
    logging.addLevelName(
        logging.INFO,
        '\033[1;32m%s\033[1;0m' % logging.getLevelName(logging.INFO),
    )
    logging.addLevelName(
        logging.DEBUG,
        '\033[1;35m%s\033[1;0m' % logging.getLevelName(logging.DEBUG),
    )

