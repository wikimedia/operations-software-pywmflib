"""Vulture whitelist to avoid false positives."""


class Whitelist:
    """Helper class that allows mocking Python objects."""

    def __getattr__(self, _):
        """Mocking magic method __getattr__."""


whitelist_logging = Whitelist()
whitelist_logging.raiseExceptions

# Needed for vulture < 0.27
whitelist_mock = Whitelist()
whitelist_mock.return_value
whitelist_mock.side_effect

whitelist_tests = Whitelist()
whitelist_tests.unit.test_confctl.TestDns.setup_method
