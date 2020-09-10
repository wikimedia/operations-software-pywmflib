"""Exceptions module."""


class WmflibError(Exception):
    """Parent exception class for all wmflib exceptions."""


class WmflibCheckError(WmflibError):
    """Parent exception class for all wmflib exceptions regarding checks.

    Particularly useful when some write action is performed and then checked but in dry-run mode, as in this mode the
    write action will not actually change anything and the check will then fail, but should catchable separately from
    the other potential exceptions that could be raised.
    """
