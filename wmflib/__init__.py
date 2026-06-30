"""wmflib package."""

import os
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
    """:py:class:`str`: the version of the current wmflib package."""
except PackageNotFoundError:  # pragma: no cover - this happens only if the package is not installed
    # Support the use case of the Debian building system where tests are run without installation. If the package is
    # not installed and the env variable is not set, re-raise so that the failure is clear and points to the cause
    # instead of leaving __version__ undefined and failing later with an obscure ImportError on `from wmflib import
    # __version__`.
    if "SETUPTOOLS_SCM_PRETEND_VERSION" not in os.environ:
        raise
    __version__ = os.environ["SETUPTOOLS_SCM_PRETEND_VERSION"]
