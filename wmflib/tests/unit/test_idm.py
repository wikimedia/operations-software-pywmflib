"""IDM utils module tests."""
from argparse import Namespace
from unittest.mock import patch

import pytest

from wmflib.idm import IdmValueError, logoutd_args, LogoutdBase


def test_logoutd_args_no_description():
    """Test the argparsing function with no description."""
    with pytest.raises(IdmValueError, match='Must provide a string description'):
        logoutd_args()


def test_logoutd_args_list():
    """Test the argparsing function for the query action."""
    args = logoutd_args('foo', ['list'])
    assert args == Namespace(command='list', verbose=0)


def test_logoutd_args_logout():
    """Test the argparsing function for the query action."""
    args = logoutd_args('foo', ['-vv', 'query', '--cn', 'bill', '--uid', 'Bill'])
    assert args == Namespace(command='query', verbose=2, cn='bill', uid='Bill')


def test_logoutd_args():
    """Test the argparsing function for the logout action."""
    args = logoutd_args('foo', ['logout', '-u', 'bob', '--cn', 'Bob'])
    assert args == Namespace(command='logout', uid='bob', verbose=0, cn='Bob')


class ConcreteLogoutdBase(LogoutdBase):
    """Example logout class."""

    def logout_user(self, user):
        """Logout user."""
        return 'logout ' + user

    def query_user(self, user):
        """Query user."""
        return 'query ' + user

    def list(self):
        """List users."""
        return 'list'


class TestLogoutd:
    """Test the logoutd class."""

    @patch(
        'argparse.ArgumentParser.parse_args',
        return_value=Namespace(uid='uid', cn='common_name', command='query'),
    )
    def setup_method(self, _, _mock_args):
        """Configure the instance."""
        # pylint: disable=attribute-defined-outside-init
        self.idm = ConcreteLogoutdBase()

    def test_user(self):
        """By Default the user identifier should return the common_name."""
        assert self.idm.user == 'common_name'

    def test_user_identifier_uid(self):
        """Update the user identifier to use the uid."""
        self.idm.user_identifier = 'uid'
        assert self.idm.user == 'uid'

    def test_query_user(self):
        """Test query user function."""
        assert self.idm.query_user(self.idm.user) == 'query common_name'

    def test_logout_user(self):
        """Test logout user function."""
        assert self.idm.logout_user(self.idm.user) == 'logout common_name'

    def test_list(self):
        """Test list function."""
        assert self.idm.list() == 'list'

    def test_run(self):
        """Test run function."""
        assert self.idm.run() == 'query common_name'


@pytest.mark.parametrize(
    'args, expected',
    (
        (
            ['query', '--uid', 'uid', '--cn', 'common_name'],
            'query common_name',
        ),
        (
            ['logout', '--uid', 'uid', '--cn', 'common_name'],
            'logout common_name',
        ),
        (['list'], 'list'),
    ),
)
def test_logoutd_run_command_argument(args, expected):
    """Test the result of the run method with different command arguments."""
    idm = ConcreteLogoutdBase(args)
    assert idm.run() == expected


def test_run_logoutd_invalid_command():
    """Test invalid command."""
    with pytest.raises(SystemExit):
        ConcreteLogoutdBase(['invalid'])
