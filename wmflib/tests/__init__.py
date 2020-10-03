"""Tests package for wmflib."""

import logging
import os

import pytest

from pkg_resources import parse_version

CAPLOG_MIN_VERSION = '3.3.0'
TESTS_BASE_PATH = os.path.realpath(os.path.dirname(__file__))


def get_fixture_path(*paths):
    """Return the absolute path of the given fixture.

    Arguments:
        *paths: arbitrary positional arguments used to compose the absolute path to the fixture.

    Returns:
        str: the absolute path of the selected fixture.

    """
    return os.path.join(TESTS_BASE_PATH, 'fixtures', *paths)


require_caplog = pytest.mark.skipif(  # pylint: disable=invalid-name
    parse_version(pytest.__version__) < parse_version(CAPLOG_MIN_VERSION), reason='Requires caplog fixture')


def check_logs(logs, message, level):
    """Assert that a log record with the given message and level is present."""
    for record in logs.records:
        if message in record.getMessage():
            assert record.levelno == level
            break
    else:
        raise RuntimeError("{level} log record with message '{msg}' not found".format(
            level=logging.getLevelName(level), msg=message))
