"""Phabricator module."""

import configparser
import logging

import phabricator

from wmflib.exceptions import WmflibError

logger = logging.getLogger(__name__)


def create_phabricator(
    bot_config_file: str, *, section: str = "phabricator_bot", dry_run: bool = True
) -> phabricator.Phabricator:
    """Initialize the Phabricator client from the bot config file.

    Examples:
        ::

            from wmflib.phabricator import create_phabricator

            phab_client = create_phabricator("/path/to/config.ini", dry_run=False)
            phab_client.task_comment("T12345", "Message")

    Arguments:
        bot_config_file (str): the path to the configuration file for the Phabricator bot, with the following
            structure::

                [section_name]
                host = https://phabricator.example.com/api/
                username = phab-bot
                token = api-12345

        section (str, optional): the name of the section of the configuration file where to find the required
            parameters.
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

    return Phabricator(client, dry_run=dry_run)


class PhabricatorError(WmflibError):
    """Custom exception class for errors of the Phabricator class."""


class Phabricator:
    """Class to interact with a Phabricator website."""

    def __init__(self, phabricator_client: phabricator.Phabricator, *, dry_run: bool = True) -> None:
        """Initialize the Phabricator client from the bot config file.

        Arguments:
            phabricator_client (phabricator.Phabricator): a Phabricator client instance.
            dry_run (bool, optional): whether this is a DRY-RUN.

        """
        self._client = phabricator_client
        self._dry_run = dry_run

    def task_comment(self, task_id: str, comment: str) -> None:
        """Add a comment on a Phabricator task.

        Arguments:
            task_id (str): the Phabricator task ID (e.g. ``T12345``) to be updated.
            comment (str): the message to add to the task.

        Raises:
            wmflib.phabricator.PhabricatorError: if unable to update the task.

        """
        if self._dry_run:
            logger.debug("Skip updating Phabricator task %s in DRY-RUN with comment: %s", task_id, comment)
            return

        try:
            transactions = [{"type": "comment", "value": comment}]
            self._client.maniphest.edit(objectIdentifier=task_id, transactions=transactions)
            logger.info("Updated Phabricator task %s", task_id)
        except Exception as e:
            raise PhabricatorError(f"Unable to update Phabricator task {task_id}") from e
