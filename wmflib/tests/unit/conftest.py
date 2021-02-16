"""Pytest customization for unit tests."""
import fcntl
import uuid

import pytest


@pytest.fixture
def locked_file(tmp_path):
    """Pytest fixture that creates a random file and locks it exclusively."""
    tmp_file = tmp_path / str(uuid.uuid4())
    with open(tmp_file, 'w') as fd:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield tmp_file
        fcntl.flock(fd, fcntl.LOCK_UN)
