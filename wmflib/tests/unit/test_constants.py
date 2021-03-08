"""Constants module tests."""

from wmflib.constants import ALL_DATACENTERS, DATACENTER_NUMBERING_PREFIX


def test_datacenters():
    """Verify both datacenter constants are in sync."""
    assert set(ALL_DATACENTERS) == set(DATACENTER_NUMBERING_PREFIX)
