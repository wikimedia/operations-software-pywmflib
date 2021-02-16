"""File I/O module tests."""
import fcntl

from unittest import mock

import pytest

from wmflib.fileio import locked_open, LockError


def try_lock_file(test_file):
    """Try to get an exclusive lock in the given file. Return True on success, False on failure."""
    with open(test_file) as fd:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return True
        except OSError:
            return False


@mock.patch('wmflib.decorators.time.sleep', return_value=None)
def test_locked_open_success(mocked_sleep, tmp_path):
    """It should acquire an exclusive lock to a file and write to it."""
    test_file = tmp_path / 'acquire_lock'
    with locked_open(test_file, 'w') as fd:
        fd.write('some text')
        assert not try_lock_file(test_file)

    assert try_lock_file(test_file)
    assert test_file.read_text() == 'some text'
    mocked_sleep.assert_not_called()


@mock.patch('wmflib.decorators.time.sleep', return_value=None)
def test_locked_open_fail(mocked_sleep, locked_file):
    """It should retry to get an exclusive lock and raise a LockError exception on failure."""
    with pytest.raises(LockError, match='Unable to acquire exclusive lock on'):
        with locked_open(locked_file):
            assert False, 'Execution should not reach this point'

    mocked_sleep.assert_has_calls([mock.call(1.0)] * 9)  # 10 tries, 9 sleeps
