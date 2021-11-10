"""Actions module."""
import logging

from typing import Hashable, List


logger = logging.getLogger(__name__)


class Actions:
    """Class to keep track and log a set of actions performed and their result with a nice string representation."""

    def __init__(self, name: Hashable):
        """The instance gets initialized with the given name, that can represent a host or any other identifier.

        It allows to save actions performed on the given name with their status (success, warning, failure).
        It exposes the following public properties:

        - ``name``: the name passed to the instance at instantiation time.

        - ``has_warnings``: a :py:class:`bool` that is :py:data:`True` when at least one warning action was registered,
          :py:data:`False` otherwise.

        - ``has_failures``: a :py:class:`bool` that is :py:data:`True` when at least one failed action was registered,
          :py:data:`False` otherwise.

        When converted to a string it returns a nicely formatted representation of the instance and all its actions
        that can be used as-is in Phabricator::

            <name> (**<status>**)
              - <action1>
              - <action2>
              - ...

        The status is enclosed in double asterisks to be rendered as bold in Phabricator.

        Examples:
            ::

                actions = Actions('host1001')
                actions.success('Downtimed on Icinga')
                actions.success('Restarted ntp')
                print(actions)

            The above code will print::

                host1001 (**PASS**)
                  - Downtimed on Icinga
                  - Restarted ntp

        Arguments:
            name (typing.Hashable): the name of the set of actions to be registered.

        """
        self.name = name
        self.actions: List[str] = []
        self.has_warnings = False
        self.has_failures = False

    def __str__(self) -> str:
        """Custom string representation of the actions performed.

        Returns:
            str: the string representation.

        """
        actions = '\n'.join(f'  - {action}' for action in self.actions)
        return f'{self.name} (**{self.status}**)\n{actions}'

    @property
    def status(self) -> str:
        """Return the current status of the actions based on the worst result recorded.

        Returns:
            str:
                * ``FAIL``: if there was at least one failure action registered
                * ``WARN`` if there was at least one warning action and no ``FAIL`` actions registered
                * ``PASS`` if only success actions were registered

        """
        if self.has_failures:
            return 'FAIL'
        if self.has_warnings:
            return 'WARN'

        return 'PASS'

    def success(self, message: str) -> None:
        """Register a successful action, it gets also logged with info level.

        Arguments:
            message (str): the action description.

        """
        self._action(logging.INFO, message)

    def failure(self, message: str) -> None:
        """Register a failed action, it gets also logged with error level.

        Arguments:
            message (str): the action description.

        """
        self._action(logging.ERROR, message)
        self.has_failures = True

    def warning(self, message: str) -> None:
        """Register an action that require some attention, it gets also logged with warning level.

        Arguments:
            message (str): the action description.

        """
        self._action(logging.WARNING, message)
        self.has_warnings = True

    def _action(self, level: int, message: str) -> None:
        """Register a generic action.

        Arguments:
            level (int): a logging level integer to register the action for.
            message (str): the action description.

        """
        logger.log(level, message)
        self.actions.append(message)


class ActionsDict(dict):
    """Custom dictionary with defaultdict capabilities for the :py:class:`wmflib.actions.Action` class.

    Automatically instantiate and returns a new instance of the :py:class:`wmflib.actions.Actions` class for every
    missing key like a :py:class:`collections.defaultdict`.

    When accessing a missing key, the key itself is passed to the new :py:class:`wmflib.actions.Actions` instance
    as ``name``.

    When converted to string returns a nicely formatted representation of the instance and all its items, that can be
    used as-is in Phabricator.

    Examples:
        ::

            actions = ActionsDict()
            actions['host1001'].success('Downtimed on Icinga')
            actions['host1001'].failure('**Failed to restart ntp**')  # Will be rendered in bold in Phabricator
            actions['host2001'].warning('//Host with alerts on Icinga//')  # Will be rendered in italic in Phabricator
            print(actions)

        The above code will print::

            - host1001 (**FAIL**)
              - Downtimed on Icinga
              - **Failed to restart ntp**

            - host2001 (**WARN**)
              - //Host not optimal on Icinga//

        It will also include a final newline at the end of the block that doesn't get rendered in this documentation.

    """

    def __missing__(self, key: Hashable) -> Actions:
        """Instantiate a new Actions instance for the missing key like a defaultdict.

        Parameters as required by Python's data model, see :py:method:`object.__missing__`.

        """
        self[key] = Actions(key)
        return self[key]

    def __str__(self) -> str:
        """Custom string representation of the instance.

        Returns:
            str: the string representation of each item in the dictionary, newline-separated.

        """
        return '\n'.join(f'- {value}\n' for value in self.values())
