"""Interactive module."""
import getpass
import logging
import os
import sys

from wmflib.exceptions import WmflibError


logger = logging.getLogger(__name__)
MIN_SECRET_SIZE: int = 6


def ask_confirmation(message: str) -> None:
    """Ask the use for confirmation in interactive mode.

    Arguments:
        message (str): the message to be printed before asking for confirmation.

    Raises:
        WmflibError: on too many invalid answers or if not in a TTY.

    """
    if not sys.stdout.isatty():
        raise WmflibError('Not in a TTY, unable to ask for confirmation')

    print(message)
    print('Type "go" to proceed or "abort" to stop')

    for _ in range(3):
        resp = input('> ')
        if resp == 'go':
            break
        if resp == 'abort':
            raise WmflibError('Confirmation manually aborted.')

        print('Invalid response, please type "go" to proceed or "abort" to stop. '
              'After 3 wrong answers the task will be aborted.')
    else:
        raise WmflibError('Too many invalid confirmation answers')


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
