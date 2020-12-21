"""Interactive module tests."""
import logging

from unittest import mock

import pytest

from wmflib import interactive
from wmflib.exceptions import WmflibError
from wmflib.tests import check_logs, require_caplog


def example_division(positional: int, *, keyword: int = 1) -> int:
    """Example function to be used in the confirm_on_failure() tests.

    - When passing keyword=0 will raise a ZeroDivisionError
    - When passing 0 to the positional argument will raise a wmflib.interactive.AbortError
    - In all other cases will return positional divided by keyword

    """
    if positional == 0:
        raise interactive.AbortError('Test aborted')

    return positional / keyword


@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_input_ok(mocked_isatty, mocked_input, capsys):
    """Calling ask_input() should return the user input if valid."""
    valid_answer = 'valid'
    mocked_isatty.return_value = True
    mocked_input.return_value = valid_answer
    message = 'Test message'
    choice = interactive.ask_input(message, [valid_answer, 'other'])
    assert choice == valid_answer
    out, _ = capsys.readouterr()
    assert message in out
    assert 'Invalid response' not in out


@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_input_ko(mocked_isatty, mocked_input, capsys):
    """Calling ask_input() should raise InputError if the correct answer is not provided."""
    mocked_isatty.return_value = True
    mocked_input.return_value = 'invalid'
    message = 'Test message'
    with pytest.raises(interactive.InputError, match='Too many invalid answers'):
        interactive.ask_input(message, ['go'])

    out, _ = capsys.readouterr()
    assert message in out
    assert out.count('Invalid response') == 3


@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_ask_input_no_tty(mocked_isatty):
    """It should raise InputError if not in a TTY."""
    mocked_isatty.return_value = False
    with pytest.raises(interactive.InputError, match='Not in a TTY, unable to ask for input'):
        interactive.ask_input('message', [])


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
    """Calling ask_confirmation() should raise AbortError if 'abort' is provided."""
    mocked_isatty.return_value = True
    mocked_input.return_value = 'abort'
    message = 'Test message'
    with pytest.raises(interactive.AbortError, match='Confirmation manually aborted'):
        interactive.ask_confirmation(message)


def test_confirm_on_failure_ok():
    """Calling confirm_on_failure() should run the given function and return its value if no exception is raised."""
    ret = interactive.confirm_on_failure(example_division, 4, keyword=2)
    assert ret == 2


@require_caplog
@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_confirm_on_failure_abort(mocked_isatty, mocked_input, capsys, caplog):
    """It should ask for input if the called function raises an exception and allow to abort it."""
    caplog.set_level(logging.INFO)
    mocked_isatty.return_value = True
    mocked_input.return_value = 'abort'
    with pytest.raises(interactive.AbortError, match='Task manually aborted'):
        interactive.confirm_on_failure(example_division, 1, keyword=0)

    out, _ = capsys.readouterr()
    assert 'What do you want to do' in out
    check_logs(caplog, 'Failed to run wmflib.tests.unit.test_interactive.example_division', logging.ERROR)


@require_caplog
def test_confirm_on_failure_func_abort(capsys, caplog):
    """It should let an AbortError exception raised in the called function pass through, not asking the user twice."""
    caplog.set_level(logging.INFO)
    with pytest.raises(interactive.AbortError, match='Test aborted'):
        interactive.confirm_on_failure(example_division, 0, keyword=1)

    out, _ = capsys.readouterr()
    assert 'What do you want to do' not in out
    log_message = 'Failed to run wmflib.tests.unit.test_interactive.example_division'
    try:
        check_logs(caplog, log_message, logging.ERROR)
        raise AssertionError('Found unexpected message in logs: {msg}'.format(msg=log_message))
    except RuntimeError:
        pass  # No log message found, as expected


@require_caplog
@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_confirm_on_failure_skip(mocked_isatty, mocked_input, capsys, caplog):
    """It should ask for input if the called function raises an exception and allow to skip it returning None."""
    mocked_isatty.return_value = True
    mocked_input.return_value = 'skip'

    ret = interactive.confirm_on_failure(example_division, 1, keyword=0)

    assert ret is None
    out, _ = capsys.readouterr()
    assert 'What do you want to do' in out
    check_logs(caplog, 'Failed to run wmflib.tests.unit.test_interactive.example_division', logging.ERROR)


@require_caplog
@mock.patch('builtins.input')
@mock.patch('wmflib.interactive.sys.stdout.isatty')
def test_confirm_on_failure_retry(mocked_isatty, mocked_input, capsys, caplog):
    """It should ask for input if the called function raises an exception and allow to skip it returning None."""
    mocked_isatty.return_value = True
    mocked_input.side_effect = ('retry', 'retry', 'skip')

    ret = interactive.confirm_on_failure(example_division, 1, keyword=0)

    assert ret is None
    out, _ = capsys.readouterr()
    assert 'What do you want to do' in out
    check_logs(caplog, 'Failed to run wmflib.tests.unit.test_interactive.example_division', logging.ERROR)


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
