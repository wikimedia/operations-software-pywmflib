wmflib Changelog
----------------

`v0.0.8`_ (2021-06-23)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""

* idm: add a new ``idm`` module with support for global logout (`T283242`_):

  * To ensure that all Python logout scripts will have the same set of arguments and to reduce everyone repeating
    the same argparse block, a ``LogoutdBase`` abstract class was added.
  * It features also a ``logoutd_args()`` function that provides the common argparse setup for all the logoutd scripts.
  * See the module's documentation for example usages.

Minor improvements
""""""""""""""""""

* constants: add ``DATACENTER_NUMBERING_PREFIX`` constant to map datacenter names to their numbering prefix used in
  hostnames.

Bug fixes
"""""""""

* interactive: also check term for tmux in ``ensure_shell_is_durable()``.
* tests: fix pip backtracking moving prospector tests to their own virtual environments.

Miscellanea
"""""""""""

* Add official support for Python 3.9
* fileio: uniform quotes used in the file.
* setup.py: add types dependencies for mypy for the dependencies that don't have yet type hints.
* CHANGELOG: fix typo in the v0.0.7 release notes.

`v0.0.7`_ (2021-02-18)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""

* dns: update DNS to support multiple namservers.

  * This allows cookbooks to configure the Dns with multiple nameservers, for example:

    .. code-block:: python

        dns = Dns(nameserver_addresses=['91.198.174.239', '208.80.153.231'])

    and thus allow users to get authoritative answers whiles also making use of DNS failover to account for any on
    going work on a specific nameserver while the cookbook is running.

    The ``PUBLIC_AUTHDNS`` constant holds the auth server ips, given that they change very infrequently.

* fileio: add new module to manage file I/O operations.

  * Add a ``locked_open()`` context manager to open a file with an exclusive lock to be used like the buil-in
    ``open()``.

Miscellanea
"""""""""""

* tests: cover untested property in the irc module.
* CHANGELOG: fix typo.
* tests: pylint, remove unnecessary disable comments.

`v0.0.6`_ (2021-01-04)
^^^^^^^^^^^^^^^^^^^^^^

Miscellanea
"""""""""""

* doc: improve installation and introduction documentation pages and some modules documentation.
* type hints: mark the package as type hinted so that mypy can recognize its type hints when imported in other
  projects.

`v0.0.5`_ (2020-12-21)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""
* Port the decorators module from Spicerack (`T257905`_).
* Port the interactive module from Spicerack (`T257905`_).
* Port the prometheus module from Spicerack (`T257905`_).
* Port the IRC logger handler from Spickerack into an irc module (`T257905`_).
* interactive: improve confirmation capabilities

  * Add a ``ask_input()`` generic function to ask the user for input and check that the answer is among a list of
    allowed choices, returning the user's choice.
  * Convert ``ask_confirmation()`` to use the ``ask_input()`` function.
  * Add an ``InputError`` and ``AbortError`` exception classes.
  * Add a ``confirm_on_failure()`` function to run any callable, and on failure ask the user to either retry, skip the
    step or abort the whole execution.

Miscellanea
"""""""""""

* docs: fix link to pywmflib Gerrit project.
* tests: fix deprecated pytest argument.

`v0.0.4`_ (2020-11-02)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""

* requests: add new requests module that exposes an ``http_session()`` function that instantiate a requests's
  ``Session`` with configurable default timeout, retry logic on some failures as well as setting a well formatted
  User-Agent.

`v0.0.3`_ (2020-10-23)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""

* Import the action module from Spicerack
* Import the config module from Spicerack
* Import the phabricator module from Spicerack

`v0.0.2`_ (2020-09-22)
^^^^^^^^^^^^^^^^^^^^^^

Miscellanea
"""""""""""

* Remove Spicerack references from docstrings.

`v0.0.1`_ (2020-07-27)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""

* Initial version of the package.
* Import the dns module and tests from Spicerack.

.. _`T257905`: https://phabricator.wikimedia.org/T257905
.. _`T283242`: https://phabricator.wikimedia.org/T283242

.. _`v0.0.1`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.1
.. _`v0.0.2`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.2
.. _`v0.0.3`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.3
.. _`v0.0.4`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.4
.. _`v0.0.5`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.5
.. _`v0.0.6`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.6
.. _`v0.0.7`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.7
.. _`v0.0.8`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.8
