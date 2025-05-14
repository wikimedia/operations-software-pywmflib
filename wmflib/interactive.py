"""Interactive module."""

import getpass
import logging
import os
import sys
import threading

from typing import Any, Callable, Optional, Sequence

from wmflib.exceptions import WmflibError


logger = logging.getLogger(__name__)
NOTIFY_LOGGER_NAME = "wmflib_interactive_notify"
"""Name of the logger used to send notifications when the process is awaiting user input."""
notify_logger = logging.getLogger(NOTIFY_LOGGER_NAME)
"""Instance of the notification logger that is used to send notification when the process is awaiting user input."""
notify_logger.propagate = False  # Prevent messages to bubble up to the parent logger if no handlers are set.
notify_logger.addHandler(logging.NullHandler())  # Prevent messages to use the root logger handlers.
MIN_SECRET_SIZE: int = 6
"""The minimum number of characters for a secret."""
NOTIFY_AFTER_SECONDS: float = 180.0
"""The amount of time in seconds after which a notification log will be triggered."""


class InputError(WmflibError):
    """Custom exception class raised on invalid input from the user in interactive mode."""


class AbortError(WmflibError):
    """Custom exception class raised when an action is manually aborted."""


def ask_input(message: str, choices: Sequence[str], *, validator: Optional[Callable[[str], None]] = None) -> str:
    """Ask the user for input in interactive mode. Can be used with a list of valid answers or a custom validator.

    If the user doesn't reply within :py:const:`wmflib.interactive.NOTIFY_AFTER_SECONDS` seconds, a notification
    message will be sent to the :py:class:`wmflib.interactive.notify_logger` logger instance at warning level.
    The client of this code is responsible of setting up the logger handler in a way to notify the user. By default
    there is a :py:class:`logging.NullHandler` handler and the messages will not be propagated to the parent logger.
    It is safe to call `notify_logger.handlers.clear()` when setting up this handler.

    Examples:
        ::

            >>> choices = ["A", "B"]
            >>> response = ask_input(f"Choose a door between {choices}", choices)
            ==> Choose a door between ['A', 'B']
            > a
            ==> Invalid response, please type one of: A,B. After 3 wrong answers the task will be aborted.
            > A
            >>> response
            'A'

            >>> def my_validator(answer: str) -> None:
            ...     if len(answer) < 5:
            ...         raise RuntimeError("The directory name must be at least 5 characters long")
            ...
            >>> response = ask_input(f"Provide a directory name", choices=[], validator=my_validator)
            ==> Provide a directory name
            > tmp
            ==> Invalid response. The directory name must be at least 5 characters long. After 3 wrong answers the
            task will be aborted.
            > tmpdir
            >>> response
            'tmpdir'

    Arguments:
        message (str): the message to be printed before asking for confirmation.
        choices (sequence): the available choices of possible answers that the user can give. Values must be strings.
            It must be set to an empty sequence in order to use the custom validator for validating free-form answers.
        validator (callable, optional): a custom validator callable that accepts a single string parameter as input and
            returns :py:data:`None` if the answer is valid and raises any Exception with a meaningful message if the
            answer is invalid. When using a custom validator the `choices` argument must be set to an empty sequence
            like an empty string.

    Returns:
        str: the selected choice or free answer if ``choices`` is set to :py:data:`None` explicitly.

    Raises:
        wmflib.interactive.InputError: if not in a TTY, invalid parameters were given or too many invalid answers
        were provided.

    """
    # TODO: once Python3.7 support is dropped use typing's Protocol and runtime_checkable for the validator
    if validator is None and not choices:
        raise InputError("The `choices` argument is empty and no custom validator was provided.")

    if validator is not None and choices:
        raise InputError("When the `validator` argument is set, the `choices` argument must be empty.")

    # pylint: disable-next=no-member,useless-suppression; https://github.com/prospector-dev/prospector/issues/677
    if not sys.stdout.isatty():
        raise InputError("Not in a TTY, unable to ask for input")

    prefix = "\x1b[36m==>\x1b[39m"  # Cyan ==> prefix
    print(f"{prefix} {message}")

    message = f"Please type one of: {','.join(choices)}"

    for _ in range(3):
        # Create a notify timer for each attempt, the user might insert an invalid answer and not see it
        timer = threading.Timer(NOTIFY_AFTER_SECONDS, notify_logger.warning, args=["is awaiting input"])
        timer.start()

        try:
            response = input("> ")

            if validator is not None:
                validator(response)
                # Log only if the answer is valid to prevent leaks, the validator must raise for invalid values
                logger.info('User input is: "%s"', response)
                return response

            if response in choices:
                logger.info('User input is: "%s"', response)  # Log only if the answer is valid to prevent leaks
                return response

        except BaseException as e:  # pylint: disable=broad-except
            # Treat any exception as invalid answer, including Ctrl+c and Ctrl+d as well as any exception raised by the
            # custom validator when present.
            if validator is not None:
                message = str(e)

        finally:
            timer.cancel()

        print(f"{prefix} Invalid response. {message}. After 3 wrong answers the task will be aborted.")

    raise InputError("Too many invalid answers")


def ask_confirmation(message: str) -> None:
    """Ask the use for confirmation in interactive mode.

    If the user doesn't reply within :py:const:`wmflib.interactive.NOTIFY_AFTER_SECONDS` seconds, a notification
    message will be sent to the :py:class:`wmflib.interactive.notify_logger` logger instance at warning level.
    The client of this code is responsible of setting up the logger handler in a way to notify the user. By default
    there is a :py:class:`logging.NullHandler` handler and the messages will not be propagated to the parent logger.
    It is safe to call `notify_logger.handlers.clear()` when setting up this handler.


    Examples:
        ::

            >>> ask_confirmation("Ready to continue?")
            ==> Ready to continue?
            Type "go" to proceed or "abort" to interrupt the execution
            > go
            >>> ask_confirmation("Ready to continue?")
            ==> Ready to continue?
            Type "go" to proceed or "abort" to interrupt the execution
            > abort
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "/usr/lib/python3/dist-packages/wmflib/interactive.py", line 69, in ask_confirmation
                raise AbortError('Confirmation manually aborted')
            wmflib.interactive.AbortError: Confirmation manually aborted

    Arguments:
        message (str): the message to be printed before asking for confirmation.

    Raises:
        wmflib.interactive.InputError: if not in a TTY or on too many invalid answers.
        wmflib.interactive.AbortError: if manually aborted.

    """
    response = ask_input(
        "\n".join((message, 'Type "go" to proceed or "abort" to interrupt the execution')), ["go", "abort"]
    )
    if response == "abort":
        raise AbortError("Confirmation manually aborted")


def confirm_on_failure(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Execute a function asking for confirmation to retry, abort or skip.

    If the user doesn't reply within :py:const:`wmflib.interactive.NOTIFY_AFTER_SECONDS` seconds, a notification
    message will be sent to the :py:class:`wmflib.interactive.notify_logger` logger instance at warning level.
    The client of this code is responsible of setting up the logger handler in a way to notify the user. By default
    there is a :py:class:`logging.NullHandler` handler and the messages will not be propagated to the parent logger.
    It is safe to call `notify_logger.handlers.clear()` when setting up this handler.


    Examples:
        ::

            >>> def test(fail=False):
            ...     if fail:
            ...         raise RuntimeError("Failed")
            ...
            >>> confirm_on_failure(test)
            >>> confirm_on_failure(test, fail=True)
            Failed to run __main__.test: Failed
            ==> What do you want to do? "retry" the last command, manually fix the issue and "skip" the last command to
                continue the execution or completely "abort" the execution.
            > retry
            Failed to run __main__.test: Failed
            ==> What do you want to do? "retry" the last command, manually fix the issue and "skip" the last command to
                continue the execution or completely "abort" the execution.
            > skip
            >>>

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
    retry_message = (
        'What do you want to do? "retry" the last command, manually fix the issue and "skip" the last '
        'command to continue the execution or completely "abort" the execution.'
    )
    choices = ["retry", "skip", "abort"]

    while True:
        try:
            ret = func(*args, **kwargs)
        except AbortError:
            raise
        except BaseException as e:  # pylint: disable=broad-except
            logger.error("Failed to run %s.%s: %s", func.__module__, func.__qualname__, e)
            logger.debug("Traceback", exc_info=True)
            response = ask_input(retry_message, choices)
            if response == "skip":
                return None
            if response == "abort":
                raise AbortError("Task manually aborted") from e
        else:
            return ret


def get_username() -> str:
    """Detect and return the name of the effective running user even if run as root.

    Examples:
        ::

            >>> get_username()
            'user'

    Returns:
        str: the name of the effective running user or ``-`` if unable to detect it.

    """
    user = os.getenv("USER")
    sudo_user = os.getenv("SUDO_USER")

    if sudo_user is not None and sudo_user != "root":
        return sudo_user

    if user is not None:
        return user

    return "-"


def ensure_shell_is_durable() -> None:
    """Ensure it is running either in non-interactive mode or in a screen/tmux session, raise otherwise.

    Examples:
        ::

            >>> ensure_shell_is_durable()  # Will raise if not in a tmux/screen session
            >>>

    Raises:
        wmflib.exceptions.WmflibError: if in a non-durable shell session.

    """
    # STY is for screen, TMUX is for tmux. Not using `getenv("NAME") is not None` to check they are not empty.
    # TODO: verify if the check on TERM is redundant.
    if (
        sys.stdout.isatty()
        and not os.getenv("STY", "")
        and not os.getenv("TMUX", "")
        and "screen" not in os.getenv("TERM", "")
        and "tmux" not in os.getenv("TERM", "")
    ):
        raise WmflibError("Must be run in non-interactive mode or inside a screen or tmux.")


def get_secret(title: str, *, confirm: bool = False) -> str:
    """Ask the user for a secret e.g. password.

    If the user doesn't reply within :py:const:`wmflib.interactive.NOTIFY_AFTER_SECONDS` seconds, a notification
    message will be sent to the :py:class:`wmflib.interactive.notify_logger` logger instance at warning level.
    The client of this code is responsible of setting up the logger handler in a way to notify the user. By default
    there are no handlers and the messages will not be propagated to the parent logger.


    Examples:
        ::

            >>> secret = get_secret("Secret key")
            Secret key:
            Secret must be at least 6 characters. try again:
            >>> secret = get_secret("Secret key", confirm=True)  # Will raise if the confirmation doesn't match
            Secret key:
            Again, just to be sure:
            >>>

    Arguments:
        title (str): The message to show the user.
        confirm (bool, optional): If :py:data:`True` ask the user to confirm the password.

    Returns:
        str: the secret.

    Raises:
        wmflib.exceptions.WmflibError: if the password confirmation does not match and confirm is :py:data:`True`.

    """
    timer = threading.Timer(NOTIFY_AFTER_SECONDS, notify_logger.warning, args=["is awaiting input"])
    timer.start()

    try:
        new_secret = getpass.getpass(prompt=f"{title}: ")

        while len(new_secret) < MIN_SECRET_SIZE:
            new_secret = getpass.getpass(prompt=f"Secret must be at least {MIN_SECRET_SIZE} characters. try again: ")

        if confirm and new_secret != getpass.getpass(prompt="Again, just to be sure: "):
            raise WmflibError(f"{title}: Passwords did not match")

        return new_secret

    finally:
        timer.cancel()
