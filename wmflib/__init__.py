"""wmflib package."""

import os
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
    """:py:class:`str`: the version of the current wmflib package."""
except PackageNotFoundError:  # pragma: no cover - this happens only if the package is not installed
    # Support the use case of the Debian building system where tests are run without installation
    if "SETUPTOOLS_SCM_PRETEND_VERSION" in os.environ:
        __version__ = os.environ["SETUPTOOLS_SCM_PRETEND_VERSION"]
