"""Interactive module tests."""
from unittest import mock

import pytest

from wmflib import interactive
from wmflib.exceptions import WmflibError


@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_confirmation_go(mocked_isatty, mocked_input, capsys):
    """Calling ask_confirmation() should not raise if the correct answer is provided."""
    mocked_isatty.return_value = True
    mocked_input.return_value = 'go'
    message = 'Test message'
    interactive.ask_confirmation(message)
    out, _ = capsys.readouterr()
    assert message in out


@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_confirmation_abort(mocked_isatty, mocked_input):
    """Calling ask_confirmation() should raise an exception if 'abort' is provided."""
    mocked_isatty.return_value = True
    mocked_input.return_value = 'abort'
    message = 'Test message'
    with pytest.raises(WmflibError, match=('Confirmation manually aborted.')):
        interactive.ask_confirmation(message)


@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_confirmation_ko(mocked_isatty, mocked_input, capsys):
    """Calling ask_confirmation() should raise if the correct answer is not provided."""
    mocked_isatty.return_value = True
    mocked_input.return_value = 'invalid'
    message = 'Test message'
    with pytest.raises(WmflibError, match='Too many invalid confirmation answers'):
        interactive.ask_confirmation(message)

    out, _ = capsys.readouterr()
    assert message in out
    assert out.count('Invalid response') == 3


@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_confirmation_no_tty(mocked_isatty):
    """It should raise WmflibError if not in a TTY."""
    mocked_isatty.return_value = False
    with pytest.raises(WmflibError, match='Not in a TTY, unable to ask for confirmation'):
        interactive.ask_confirmation('message')


def test_get_username_no_env(monkeypatch):
    """If no env variable is set should return '-'."""
    monkeypatch.delenv('USER', raising=False)
    monkeypatch.delenv('SUDO_USER', raising=False)
    assert interactive.get_username() == '-'


def test_get_username_root(monkeypatch):
    """When unable to detect the real user should return 'root'."""
    monkeypatch.setenv('USER', 'root')
    monkeypatch.delenv('SUDO_USER', raising=False)
    assert interactive.get_username() == 'root'


def test_get_username_ok(monkeypatch):
    """As a normal user with sudo should return the user's name."""
    monkeypatch.setenv('USER', 'root')
    monkeypatch.setenv('SUDO_USER', 'user')
    assert interactive.get_username() == 'user'


@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ensure_shell_is_durable_interactive(mocked_isatty):
    """Should raise WmflibError if in an interactive shell."""
    mocked_isatty.return_value = True
    with pytest.raises(WmflibError, match='Must be run in non-interactive mode or inside a screen or tmux.'):
        interactive.ensure_shell_is_durable()

    assert mocked_isatty.called


@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ensure_shell_is_durable_non_interactive(mocked_isatty):
    """Should raise WmflibError if in an interactive shell."""
    mocked_isatty.return_value = False
    interactive.ensure_shell_is_durable()
    assert mocked_isatty.called


@mock.patch('wmflib.interactive.sys.stdout.isatty')
@pytest.mark.parametrize('env_name, env_value', (
    ('STY', '12345.pts-1.host'),
    ('TMUX', '/tmux-1001/default,12345,0'),
    ('TERM', 'screen-example'),
))
def test_ensure_shell_is_durable_sty(mocked_isatty, env_name, env_value, monkeypatch):
    """Should not raise if in an interactive shell with STY set, TMUX set or a screen-line TERM."""
    mocked_isatty.return_value = True
    monkeypatch.setenv(env_name, env_value)
    interactive.ensure_shell_is_durable()
    assert mocked_isatty.called


@mock.patch('wmflib.interactive.getpass')
def test_get_secret_correct_noconfirm(mocked_getpass):
    """Should ask for secret once and return the secret."""
    mocked_getpass.getpass.return_value = 'interactive_password'
    assert interactive.get_secret('secret') == 'interactive_password'
    mocked_getpass.getpass.assert_called_once_with(prompt='secret: ')


@mock.patch('wmflib.interactive.getpass')
def test_get_secret_correct(mocked_getpass):
    """Should ask for secret twice and return the secret."""
    mocked_getpass.getpass.side_effect = ['interactive_password', 'interactive_password']
    assert interactive.get_secret('secret', confirm=True) == 'interactive_password'
    mocked_getpass.getpass.assert_has_calls(
        [mock.call(prompt='secret: '), mock.call(prompt='Again, just to be sure: ')])


@mock.patch('wmflib.interactive.getpass')
def test_get_secret_bad_retry(mocked_getpass):
    """Should ask for secret twice and raise WmflibError if they don't match."""
    mocked_getpass.getpass.side_effect = ['interactive_password', 'foobar']
    with pytest.raises(WmflibError, match='secret: Passwords did not match'):
        interactive.get_secret('secret', confirm=True)
    mocked_getpass.getpass.assert_has_calls(
        [mock.call(prompt='secret: '), mock.call(prompt='Again, just to be sure: ')])


@mock.patch('wmflib.interactive.getpass')
def test_get_secret_too_small(mocked_getpass):
    """Should ask for secret until the minimum length is met."""
    mocked_getpass.getpass.side_effect = ['5char', 'interactive_password']
    assert interactive.get_secret('secret') == 'interactive_password'
    mocked_getpass.getpass.assert_has_calls(
        [mock.call(prompt='secret: '),
         mock.call(prompt='Secret must be at least 6 characters. try again: ')])
