"""File I/O module."""
import fcntl
import logging

from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Generator, IO

from wmflib.decorators import retry
from wmflib.exceptions import WmflibError


logger = logging.getLogger(__name__)


class FileIOError(WmflibError):
    """Custom exception class for errors of the BlockInFile class."""


class LockError(FileIOError):
    """Custom exception class raised when unable to exclusively lock a file."""


@contextmanager
def locked_open(file_path: Path, file_mode: str = 'r', *, timeout: int = 10) -> Generator[IO, None, None]:
    """Context manager to open a file with an exclusive lock on it and a retry logic.

    Arguments:
        file_path (pathlib.Path): the file path to open.
        file_mode (str, optional): the mode in which the file is opened, see :py:func:`open` for details.
        timeout (int, optional): the total timeout in seconds to wait to acquire the exclusive lock before giving up.
            Ten tries will be attempted to acquire the lock within the timeout.

    Raises:
        wmflib.fileio.LockError: on failure to acquire the exclusive lock on the file.

    Yields:
        file object: the open file with an exclusive lock on it.

    """
    tries = 10
    with open(file_path, file_mode) as fd:
        try:
            # Decorate the call to the locking function to retry acquiring the lock:
            # decorator(decorator_args)(function)(function_args)
            retry(
                tries=tries,
                delay=timedelta(seconds=timeout / tries),
                backoff_mode='constant',
                exceptions=(OSError, BlockingIOError)
            )(fcntl.flock)(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.debug("Acquired exclusive lock on %s", file_path)
        except OSError as e:
            raise LockError('Unable to acquire exclusive lock on {name}'.format(name=file_path)) from e

        try:
            yield fd
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            logger.debug("Released exclusive lock on %s", file_path)
