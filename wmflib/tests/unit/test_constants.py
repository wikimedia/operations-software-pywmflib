"""Constants module tests."""

from wmflib.constants import ALL_DATACENTERS, CORE_DATACENTERS, DATACENTER_NUMBERING_PREFIX, US_DATACENTERS


def test_datacenters():
    """Verify both datacenter constants are in sync."""
    assert set(ALL_DATACENTERS) == set(DATACENTER_NUMBERING_PREFIX)


def test_core_datacenters():
    """Verify that the core datacenters is a subset of all datacenters."""
    assert set(CORE_DATACENTERS).issubset(set(ALL_DATACENTERS))


def test_us_datacenters():
    """Verify that the US datacenters are a subset of all datacenters."""
    assert set(US_DATACENTERS).issubset(set(ALL_DATACENTERS))
