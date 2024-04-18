"""Constants module."""


ALL_DATACENTERS = ('eqiad', 'codfw', 'esams', 'ulsfo', 'eqsin', 'drmrs', 'magru')
"""tuple: all WMF datacenters."""


CORE_DATACENTERS = ("eqiad", "codfw")
"""tuple: WMF core datacenters."""


PUBLIC_AUTHDNS = ('208.80.154.238', '208.80.153.231', '198.35.27.27')
"""tuple: publicly Authorative DNS servers for the WMF domains."""


DATACENTER_NUMBERING_PREFIX = {
    'eqiad': '1',
    'codfw': '2',
    'esams': '3',
    'ulsfo': '4',
    'eqsin': '5',
    'drmrs': '6',
    'magru': '7',
}
"""dict: mapping of hostname prefix for numbered servers for each WMF datacenter."""
