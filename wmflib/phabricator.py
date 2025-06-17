"""Phabricator module."""

import configparser
import logging
import re

import phabricator

from wmflib.exceptions import WmflibError

logger = logging.getLogger(__name__)


def create_phabricator(
    bot_config_file: str,
    *,
    section: str = "phabricator_bot",
    allow_empty_identifiers: bool = False,
    dry_run: bool = True,
) -> phabricator.Phabricator:
    """Initialize the Phabricator client from the bot config file.

    Examples:
        ::

            >>> from wmflib.phabricator import create_phabricator, Phabricator
            >>> phab_client = create_phabricator("/path/to/config.ini", dry_run=False)
            >>> Phabricator.validate_task_id("T12345")
            'T12345'
            >>> if phab_client.task_accessible("T12345"):
            ...     phab_client.task_comment("T12345", "Message")

    Arguments:
        bot_config_file (str): the path to the configuration file for the Phabricator bot, with the following
            structure::

                [section_name]
                host = https://phabricator.example.com/api/
                username = phab-bot
                token = api-12345

        section (str, optional): the name of the section of the configuration file where to find the required
            parameters.
        allow_empty_identifiers: if set to :py:data:`True` all the methods that require an ID (e.g. a task ID) will
            also accept an empty string as identifier and act as noop in that case.
        dry_run (bool, optional): whether this is a DRY-RUN.

    Returns:
        wmflib.phabricator.Phabricator: a Phabricator instance.

    Raises:
        wmflib.phabricator.PhabricatorError: if unable to get all the required parameters from the bot configuration
            file, or to initialize the Phabricator client.

    """
    parser = configparser.ConfigParser()
    parser.read(bot_config_file)
    required_options = ("host", "username", "token")
    params = {}

    try:
        for option in required_options:
            params[option] = parser.get(section, option)
    except configparser.NoSectionError as e:
        raise PhabricatorError(f"Unable to find section {section} in config file {bot_config_file}") from e
    except configparser.NoOptionError as e:
        raise PhabricatorError(
            f"Unable to find all required options {required_options} in section {section} of config "
            f"file {bot_config_file}"
        ) from e

    try:
        client = phabricator.Phabricator(**params)
    except Exception as e:
        raise PhabricatorError("Unable to instantiate Phabricator client") from e

    return Phabricator(client, allow_empty_identifiers=allow_empty_identifiers, dry_run=dry_run)


def validate_task_id(task_id: str, *, allow_empty_identifiers: bool = False) -> str:
    r"""Phabricator task ID validator suitable to be used with :py:meth:`argparse.ArgumentParser.add_argument`.

    Ensures that the task ID is properly formatted as T123456. Empty string are also accepted when setting
    ``allow_empty_identifiers=True``, suitable to be used with argparse when the argument is optional with
    a default value of empty string.

    Examples:
    ::

        >>> validate_task_id("T1")
        'T1'
        >>> validate_task_id("T999999")
        'T999999'
        >>> validate_task_id("", allow_empty_identifiers=True)
        ''
        >>> validate_task_id("T1234567")
        Traceback (most recent call last):
          [...SNIP...]
        ValueError: Invalid Phabricator task ID, expected to match pattern 'T\d{1,6}$', got 'T1234567'

    Arguments:
        task_id: the Phabricator task ID to validate.
        allow_empty_identifiers: if set to :py:data:`True` will consider an empty task as valid.

    Raises:
        ValueError: if the ``task_id`` is not properly formatted, so that argparse will properly format the error
            message. See also the :py:meth:`argparse.ArgumentParser.add_argument` documentation.

    Returns:
        the task ID if valid.

    """
    if allow_empty_identifiers and not task_id:  # Accept empty strings
        return task_id

    pattern = r"T\d{1,6}$"
    if re.match(pattern, task_id) is None:
        raise ValueError(f"Invalid Phabricator task ID, expected to match pattern '{pattern}', got '{task_id}'")

    return task_id


class PhabricatorError(WmflibError):
    """Custom exception class for errors of the Phabricator class."""


class Phabricator:
    """Class to interact with a Phabricator website."""

    def __init__(
        self,
        phabricator_client: phabricator.Phabricator,
        *,
        dry_run: bool = True,
        allow_empty_identifiers: bool = False,
    ) -> None:
        """Initialize the Phabricator client from the bot config file.

        Arguments:
            phabricator_client (phabricator.Phabricator): a Phabricator client instance.
            dry_run (bool, optional): whether this is a DRY-RUN.
            allow_empty_identifiers: if set to :py:data:`True` all the methods that require an ID (e.g. a task ID) will
                also accept an empty string as identifier and act as noop in that case.

        """
        self._client = phabricator_client
        self._dry_run = dry_run
        self._allow_empty_identifiers = allow_empty_identifiers

    def task_accessible(self, task_id: str, *, raises: bool = True) -> bool:
        """Check if a task exists and is accessible to the curirent API user.

        Examples:
        ::

            >>> phab_client.task_accessible("T1")
            True
            >>> phab_client.task_accessible("T1", raises=False)
            True
            >>> phab_client.task_accessible("T999999")
            False
            >>> phab_client.task_accessible("")  # with allow_empty_identifiers=True
            DEBUG:wmflib.phabricator:No task specified and allow_empty_identifiers=True, nothing to check
            False
            >>> phab_client.task_accessible("", raises=False)  # with allow_empty_identifiers=True
            DEBUG:wmflib.phabricator:No task specified and allow_empty_identifiers=True, nothing to check
            False
            >>> phab_client.task_accessible("", raises=False)  # with allow_empty_identifiers=False
            ERROR:wmflib.phabricator:Unable to determine if the task '' is accessible (raises=False): Empty task ID
            False
            >>> phab_client.task_accessible("")  # with allow_empty_identifiers=False
            Traceback (most recent call last):
              [...SNIP...]
            wmflib.phabricator.PhabricatorError: Empty task ID
              [...SNIP...]
            wmflib.phabricator.PhabricatorError: Unable to determine if the task '' is accessible
            >>> phab_client.task_accessible("T1")
            Traceback (most recent call last):
              [...SNIP...]
            phabricator.APIError: ERR-INVALID-AUTH: API token "api-a" has the wrong length. [...SNIP...]
              [...SNIP...]
            wmflib.phabricator.PhabricatorError: Unable to determine if the task 'T1' is accessible
            >>> phab_client.task_accessible("T1", raises=False)
            ERROR:wmflib.phabricator:Unable to determine if the task T1 is accessible (raises=False): ERR-[...SNIP...]
            ERROR:wmflib.phabricator:Unable to determine if the task 'T1' is accessible (raises=False): ERR[...SNIP...]
            False

        Arguments:
            task_id: the Phabricator task ID (e.g. ``T12345``) to be updated. If empty string it will raise an
                exception unless ``allow_empty_identifiers`` is set to :py:data:`True`. In this case it returns
                :py:data:`False` and logs a message at debug level.
            raises: if set to :py:data:`False` does not raise an exception and returns :py:data:`False` if unable
                to check the task accessibility.

        Raises:
            wmflib.phabricator.PhabricatorError: if unable to verify if the task is accessible and ``raises`` is
                set to :py:data:`True`.

        Returns:
            :py:data:`True` if the task exists and is accessible by the current user, :py:data:`False` if not
            accessible, an empty string was passed and allow_empty_identifiers is set to :py:data:`True` or if unable
            to verify if the task is accessible and ``raises`` is set to :py:data:`False`.

        """
        if self._allow_empty_identifiers and not task_id:
            logger.debug("No task specified and allow_empty_identifiers=True, nothing to check")
            return False

        try:
            if not task_id:
                raise PhabricatorError("Empty task ID")  # noqa: TRY301

            results = self._client.maniphest.search(constraints={"ids": [int(task_id[1:])]})
            return len(results.data) == 1
        except Exception as e:
            message = f"Unable to determine if the task '{task_id}' is accessible"
            if raises:
                raise PhabricatorError(message) from e

            logger.error("%s (raises=%s): %s", message, raises, e)
            return False

    def task_comment(self, task_id: str, comment: str, *, raises: bool = True) -> None:
        """Add a comment on a Phabricator task.

        Examples:
        ::

            >>> phab_client.task_comment("T12345", "Message")
            >>> phab_client.task_comment("", "Message")  # with allow_empty_identifiers=True
            DEBUG:wmflib.phabricator:No task specified, skipping task update with comment: Message
            >>> phab_client.task_comment("", "Message", raises=False)  # with allow_empty_identifiers=True
            DEBUG:wmflib.phabricator:No task specified, skipping task update with comment: Message
            >>> phab_client.task_comment("T999999", "Message")
            Traceback (most recent call last):
              [...SNIP...]
            phabricator.APIError: ERR-CONDUIT-CORE: Monogram "T999999" does not identify a valid object.
              [...SNIP...]
            wmflib.phabricator.PhabricatorError: Unable to update Phabricator task 'T999999'
            >>> phab_client.task_comment("T999999", "Test comment", raises=False)
            ERROR:wmflib.phabricator:Unable to update Phabricator task 'T999999' (raises=False): ERR-CONDUI[...SNIP...]
            >>> phab_client.task_comment("T12345", "Message")  # with dry_run=True
            DEBUG:wmflib.phabricator:Skip updating Phabricator task 'T12345' in DRY-RUN with comment: Message

        Arguments:
            task_id (str): the Phabricator task ID (e.g. ``T12345``) to be updated. If empty string no update will be
                sent and a debug log message will be logged.
            comment (str): the message to add to the task.
            raises (bool): if set to :py:data:`False` does not raise an exception if unable to comment on the task.

        Raises:
            wmflib.phabricator.PhabricatorError: if unable to update the task and ``raises`` is set to
                :py:data:`True`.

        """
        if self._allow_empty_identifiers and not task_id:
            logger.debug("No task specified, skipping task update with comment: %s", comment)
            return

        if self._dry_run:
            logger.debug("Skip updating Phabricator task '%s' in DRY-RUN with comment: %s", task_id, comment)
            return

        try:
            if not task_id:
                raise PhabricatorError("Empty task ID")  # noqa: TRY301

            transactions = [{"type": "comment", "value": comment}]
            self._client.maniphest.edit(objectIdentifier=task_id, transactions=transactions)
            logger.info("Updated Phabricator task %s", task_id)
        except Exception as e:
            message = f"Unable to update Phabricator task '{task_id}'"
            if raises:
                raise PhabricatorError(message) from e

            logger.error("%s (raises=False): %s", message, e)
