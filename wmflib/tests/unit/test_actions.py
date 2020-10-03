"""Actions module tests."""
import logging

from textwrap import dedent

from wmflib import actions
from wmflib.tests import check_logs, require_caplog


def test_actionsdict_string_representation():
    """It should convert the instance to a nice string representation."""
    actions_dict = actions.ActionsDict()
    actions_dict['name1'].success('success1')
    actions_dict['name2'].failure('failure1')
    expected = """
    - name1 (**PASS**)
      - success1

    - name2 (**FAIL**)
      - failure1
    """
    assert dedent(expected).lstrip() == str(actions_dict)


class TestActions:
    """Test class for the Actions class."""

    def setup_method(self):
        """Initialize the test instance."""
        # pylint: disable=attribute-defined-outside-init
        self.actions = actions.Actions('name1')

    def test_default_status(self):
        """It should return a successful default status with no actions."""
        assert self.actions.status == 'PASS'
        assert not self.actions.actions

    @require_caplog
    def test_success(self, caplog):
        """It should register a success action."""
        caplog.set_level('INFO')  # Necessary until https://github.com/pytest-dev/pytest/issues/7335 is fixed
        self.actions.success('success1')
        assert self.actions.status == 'PASS'
        assert not self.actions.has_warnings
        assert not self.actions.has_failures
        assert len(self.actions.actions) == 1
        check_logs(caplog, 'success1', logging.INFO)

    @require_caplog
    def test_warning(self, caplog):
        """It should register a warning action."""
        self.actions.warning('warning1')
        self.actions.success('success1')
        assert self.actions.status == 'WARN'
        assert self.actions.has_warnings
        assert not self.actions.has_failures
        assert len(self.actions.actions) == 2
        check_logs(caplog, 'warning1', logging.WARNING)

    @require_caplog
    def test_failure(self, caplog):
        """It should register a failed action."""
        self.actions.failure('failure1')
        self.actions.success('success1')
        assert self.actions.status == 'FAIL'
        assert not self.actions.has_warnings
        assert self.actions.has_failures
        assert len(self.actions.actions) == 2
        check_logs(caplog, 'failure1', logging.ERROR)

    def test_failure_and_warning(self):
        """With a failure and a warning it should have a failed status but also report warnings."""
        self.actions.failure('failure1')
        self.actions.warning('warning1')
        self.actions.success('success1')
        assert self.actions.status == 'FAIL'
        assert self.actions.has_warnings
        assert self.actions.has_failures
        assert len(self.actions.actions) == 3

    def test_string_representation(self):
        """It should convert the instance to a nice string representation."""
        self.actions.success('success1')
        self.actions.warning('warning1')
        self.actions.failure('failure1')
        expected = """
        name1 (**FAIL**)
          - success1
          - warning1
          - failure1
        """
        assert dedent(expected).strip() == str(self.actions)
