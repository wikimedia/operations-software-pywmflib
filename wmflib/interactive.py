"""Interactive module."""
import getpass
import logging
import os
import sys

from typing import Any, Callable, Sequence

from wmflib.exceptions import WmflibError


logger = logging.getLogger(__name__)
MIN_SECRET_SIZE: int = 6


class InputError(WmflibError):
    """Custom exception class raised on invalid input from the user in interactive mode."""


class AbortError(WmflibError):
    """Custom exception class raised when an action is manually aborted."""


def ask_input(message: str, choices: Sequence[str]) -> str:
    """Ask the user for input in interactive mode.

    Arguments:
        message (str): the message to be printed before asking for confirmation.
        choices (sequence): the available choices of possible answers that the user can give. Values must be strings.

    Returns:
        str: the selected choice.

    Raises:
        wmflib.interactive.InputError: if not in a TTY or on too many invalid answers.

    """
    prefix = '\x1b[36m>>>\x1b[39m'  # Cyan >>> prefix
    if not sys.stdout.isatty():
        raise InputError('Not in a TTY, unable to ask for input')

    print('{prefix} {message}'.format(prefix=prefix, message=message))

    for _ in range(3):
        response = input('> ')
        if response in choices:
            return response

        print('{prefix} Invalid response, please type one of: {choices}. '
              'After 3 wrong answers the task will be aborted.'.format(prefix=prefix, choices=','.join(choices)))

    raise InputError('Too many invalid answers')


def ask_confirmation(message: str) -> None:
    """Ask the use for confirmation in interactive mode.

    Arguments:
        message (str): the message to be printed before asking for confirmation.

    Raises:
        wmflib.interactive.InputError: if not in a TTY or on too many invalid answers.
        wmflib.interactive.AbortError: if manually aborted.

    """
    response = ask_input('\n'.join((message, 'Type "go" to proceed or "abort" to interrupt the execution')),
                         ['go', 'abort'])
    if response == 'abort':
        raise AbortError('Confirmation manually aborted')


def confirm_on_failure(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Execute a function asking for confirmation to retry, abort or skip.

    Arguments:
        func (callable): the function/method to execute.
        *args (mixed): all the positional arguments to pass to the function/method.
        *kwargs (mixed): all the keyword arguments to pass to the function/method.

    Returns:
        mixed: what the called function returns, or :py:data:`None` if the execution should continue skipping this
        step because has been manually fixed.

    Raises:
        wmflib.interactive.AbortError: on manually aborted tasks.

    """
    retry_message = ('What do you want to do? "retry" the last command, manually fix the issue and "skip" the last '
                     'command to continue the execution or completely "abort" the execution.')
    choices = ['retry', 'skip', 'abort']

    while True:
        try:
            ret = func(*args, **kwargs)
        except AbortError:
            raise
        except BaseException as e:  # pylint: disable=broad-except
            logger.error('Failed to run %s.%s: %s', func.__module__, func.__qualname__, e)
            logger.debug('Traceback', exc_info=True)
            response = ask_input(retry_message, choices)
            if response == 'skip':
                return None
            if response == 'abort':
                raise AbortError('Task manually aborted')
        else:
            return ret


def get_username() -> str:
    """Detect and return the name of the effective running user even if run as root.

    Returns:
        str: the name of the effective running user or ``-`` if unable to detect it.

    """
    user = os.getenv('USER')
    sudo_user = os.getenv('SUDO_USER')

    if sudo_user is not None and sudo_user != 'root':
        return sudo_user

    if user is not None:
        return user

    return '-'


def ensure_shell_is_durable() -> None:
    """Ensure it is running either in non-interactive mode or in a screen/tmux session, raise otherwise.

    Raises:
        wmflib.exceptions.WmflibError: if in a non-durable shell session.

    """
    # STY is for screen, TMUX is for tmux. Not using `getenv('NAME') is not None` to check they are not empty.
    # TODO: verify if the check on TERM is redundant.
    if (sys.stdout.isatty() and not os.getenv('STY', '') and not os.getenv('TMUX', '')
            and 'screen' not in os.getenv('TERM', '')):
        raise WmflibError('Must be run in non-interactive mode or inside a screen or tmux.')


def get_secret(title: str, *, confirm: bool = False) -> str:
    """Ask the user for a secret e.g. password.

    Arguments:
        title (str): The message to show the user.
        confirm (bool, optional): If :py:data:`True` ask the user to confirm the password.

    Returns:
        str: the secret.

    """
    new_secret = getpass.getpass(prompt='{}: '.format(title))

    while len(new_secret) < MIN_SECRET_SIZE:
        new_secret = getpass.getpass(
            prompt='Secret must be at least {} characters. try again: '.format(MIN_SECRET_SIZE))

    if confirm and new_secret != getpass.getpass(prompt='Again, just to be sure: '):
        raise WmflibError('{}: Passwords did not match'.format(title))

    return new_secret
