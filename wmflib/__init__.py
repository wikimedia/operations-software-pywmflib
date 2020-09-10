"""wmflib package."""

from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__: str = get_distribution('wmflib').version  # Must be the same used as 'name' in setup.py
    """:py:class:`str`: the version of the current wmflib module."""
except DistributionNotFound:  # pragma: no cover - this should never happen during tests
    pass  # package is not installed
