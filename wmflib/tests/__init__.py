"""Tests package for wmflib."""

import logging
from pathlib import Path

TESTS_BASE_PATH = Path(__file__).parent.resolve()


def get_fixture_path(*paths):
    """Return the absolute path of the given fixture.

    Arguments:
        *paths: arbitrary positional arguments used to compose the absolute path to the fixture.

    Returns:
        str: the absolute path of the selected fixture.

    """
    return Path(TESTS_BASE_PATH, "fixtures", *paths)


def check_logs(logs, message, level):
    """Assert that a log record with the given message and level is present."""
    for record in logs.records:
        if message in record.getMessage():
            assert record.levelno == level
            break
    else:
        raise RuntimeError(f"{logging.getLevelName(level)} log record with message '{message}' not found")
