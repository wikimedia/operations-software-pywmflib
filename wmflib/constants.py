"""Constants module."""

ALL_DATACENTERS = ('eqiad', 'codfw', 'esams', 'ulsfo', 'eqsin')
"""tuple: list of all datacenters."""

PUBLIC_AUTHDNS = ('208.80.154.238', '208.80.153.231', '91.198.174.239')
"""tuple: list of publicly Authorative DNS servers for the wikimedia foundation domain portfolio"""

DATACENTER_NUMBERING_PREFIX = {
    'eqiad': '1',
    'codfw': '2',
    'esams': '3',
    'ulsfo': '4',
    'eqsin': '5',
}
"""dict: prefix for numbered servers in each datacenter."""
