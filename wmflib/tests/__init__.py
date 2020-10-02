"""Tests package for wmflib."""

import pytest

from pkg_resources import parse_version

CAPLOG_MIN_VERSION = '3.3.0'

require_caplog = pytest.mark.skipif(  # pylint: disable=invalid-name
    parse_version(pytest.__version__) < parse_version(CAPLOG_MIN_VERSION), reason='Requires caplog fixture')
