"""wmflib package."""

from contextlib import suppress

from pkg_resources import DistributionNotFound, get_distribution


with suppress(DistributionNotFound):  # Might happen only if the package is not installed, never during tests
    __version__: str = get_distribution("wmflib").version  # Must be the same used as 'name' in setup.py
    """:py:class:`str`: the version of the current wmflib package."""
