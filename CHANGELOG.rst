wmflib Changelog
----------------

`v1.2.6`_ (2024-09-05)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* interactive: fix regression and log the user input only if is valid to prevent leaks in the logs of wrongly pasted
  inputs.

Miscellanea
"""""""""""

* setup.py: fix test dependency removed upstream.

`v1.2.5`_ (2024-04-18)
^^^^^^^^^^^^^^^^^^^^^^

Minor improvements
""""""""""""""""""

constants: add the new magru datacenter.

`v1.2.4`_ (2023-11-28)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* constants: update ``ns2.wikimedia.org`` IP address as it was recently changed.
* requests: fix import of urllib's ``Retry`` to be imported directly instead of importing it from requests to avoid
  mypy confusion.

Miscellanea
"""""""""""

* documentation: extend the ``@retry`` decorator documentation adding the formula to calculate the total delay given
  the number of tries and the delay argument for the different backoff strategies.
* tox.ini: use directly ``sphinx-build`` instead of ``setup.py`` to generate the documentation, this prevents a
  deprecation warning or failure with the newest Sphinx.
* tox.ini: remove optimization for tox <4. Tox 4 will not re-use the environments because of the different names,
  so removing this tox <4 optimization as it's making subsequent runs slower with tox 4+.

`v1.2.3`_ (2023-07-31)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* irc: handle custom logging formatters, when set allow the message to be formatted according to them.

Miscellanea
"""""""""""

* irc: refactored code and tests to simplify the code and improve readability.

`v1.2.2`_ (2023-04-27)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* dns: clarify the type of the ``nameserver_addresses`` argument of the Dns class to adhere to the dnspython one.
* dns: convert the sequence of ``nameserver_addresses`` to list to adhere to what dnspython is expecting.
* requests: rename the type alias ``TypeTimeout`` to ``TimeoutType`` to adhere to pylint naming formats.

Miscellanea
"""""""""""

* tox: disable bandit's ``request_without_timeout`` check in tests due to false positives.

`v1.2.1`_ (2023-02-02)
^^^^^^^^^^^^^^^^^^^^^^

Minor improvements
""""""""""""""""""

* interactive: log the response to ``ask_input`` for easier troubleshooting. Indirectly logs also the response to
  ``ask_confirmation`` and ``confirm_on_failure``.
* interactive: allow free responses in ``ask_input`` (`T327408`_):

  * Allow the answer to ``ask_input`` to be free-form using a custom validator callable.
  * The choices argument must be set to an empty sequence when the custom validator is set.
  * Add additional validation to fail in case choices is empty and no validator is provided or if the choices argument
    is non empty and the validator one is also set.

* requests: allow to skip the session retry logic. In some cases, for example when using the ``@retry`` decorator from
  the decorators module, a client code might want to just set the UA and the timeout without any retry logic.

Miscellanea
"""""""""""

* prometheus: fix typo in docstring.
* doc: set default language.
* doc: update URL to requests library timeouts documetation page.
* Add configuration file for the WMF-specific release script.
* flake8: move all flake8 config to ``setup.cfg``.
* tox: add ``--no-external-config`` to prospector.
* tests: remove unnecessary pylint disable
* setup.py: specify ``python_requires``.
* setup.py: add support for Python 3.10 and 3.11.
* setup.py: force a newer ``sphinx_rtd_theme`` to avoid a rendering bug of the older version.

`v1.2.0`_ (2022-04-04)
^^^^^^^^^^^^^^^^^^^^^^

New features
""""""""""""

* prometheus: add support for Thanos

  * Extract the common functionalities into a ``PrometheusBase`` class.
  * Have the existing ``Prometheus`` class inherit from ``PrometheusBase``.
  * Add a new ``Thanos`` class that inherits from ``PrometheusBase`` to query the Thanos endpoint.
  * For Thanos queries set the deduplicate parameter always to ``true`` and the partial response one always to false to
    ensure to have unique data and all the data, respectively.
  * See also the `Thanos#Global_view`_ Wikitech page.

Minor improvements
""""""""""""""""""

* prometheus: allow to specify a different Prometheus instance from the default ``ops`` one, while keeping backward
  compatibility.

Bug fixes
"""""""""

* interactive: catch ``Ctrl+c`` / ``Ctrl+d`` on ``ask_input()`` to handle them properly.

Miscellanea
"""""""""""

* requests: fix docstring regarding the timeout type.

`v1.1.2`_ (2022-03-09)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* requests: fix backward compatibility with urllib3 also in the tests.

`v1.1.1`_ (2022-03-09)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* requests: fix backward compatibility with urllib3

  * Versions before 1.26.0 accept only the old parameter name 'method_whitelist', that will be removed in version 2.0.
  * Keep backward compatibility with previous versions of urllib3.

`v1.1.0`_ (2022-03-09)
^^^^^^^^^^^^^^^^^^^^^^

Minor improvements
""""""""""""""""""

* requests: allow to customize the list of HTTP methods and HTTP status codes that should trigger a retry as the
  existing generic values might need to be tweaked at times.

Miscellanea
"""""""""""

* prospector: ignore deprecation message

  * The latest ``prospector`` issues a deprecated message for the ``pep8`` and ``pep257`` tools that have been renamed
    to ``pycodestyle`` and ``pydocstyle`` respectively. The new names are incompatible with ``prospector < 1.7.0``,
    so for now keep the old names and disable the deprecation warning.

`v1.0.2`_ (2022-02-14)
^^^^^^^^^^^^^^^^^^^^^^

Bug fixes
"""""""""

* requests: fix timeout parameter of ``http_session()`` so that is gets always propagated to the underlying calls to
  the requests library as that was not always the case. Clarify in the documentation how to unset the timeout for a
  single call when using this session.

`v1.0.1`_ (2022-02-09)
^^^^^^^^^^^^^^^^^^^^^^

Minor improvements
""""""""""""""""""

* requests: add support to specify connection and read timeouts separately.

    * Set the default connection timeout to 3s and keep the existing read timeout to 5s.

Miscellanea
"""""""""""

* setup.py: temporarily add upper limit to dnspython, the latest 2.2.0 version generates mypy issues.

`v1.0.0`_ (2021-11-11)
^^^^^^^^^^^^^^^^^^^^^^

Minor improvements
""""""""""""""""""

* constants: add the new ``drmrs`` datacenter to existing constants.
* constants: add ``CORE_DATACENTERS`` constant currently defined in Spicerack.
* Adopt ``pathlib.Path`` everywhere in the project:

  * Accept both ``str`` and ``os.PathLike`` objects in the ``config`` and ``fileio`` modules for file name parameters.
  * Use ``pathlib.Path`` instead of the ``os.path`` functions across the project.

* style: adopt f-strings, converting all ``format()`` calls to f-strings when feasible.

* interactive: change input prefix to ``==>``:

  * Change the input prefix from ``>>>`` to ``==>`` to allow for code examples in an interactive Python console to be
    used in docstrings as documentation without having issues with the syntax highlighter.

* docs: add usage examples to all modules.

Miscellanea
"""""""""""

* versioning: fully adopt semantic versioning starting with this release.
* pylint: fix newly reported issues.

`v0.0.9`_ (2021-08-04)
^^^^^^^^^^^^^^^^^^^^^^

Minor improvements
""""""""""""""""""

* decorators: improve the ``@retry`` decorator.

  * Add a new optional ``dynamic_params_callbacks`` parameter to the ``@retry`` decorator.
  * This parameter accepts a tuple of callbacks that will be called by the decorator and allow them to modify the
    parameters of the decorator itself at runtime.
  * Fix the signature of retry now that the upstream bug in pylint has been fixed and the newer version is included in
    prospector. This allows to remove some type ingore that were required before.

* idm: make the ``cn`` and ``uid`` arguments of ``logoutd_args()`` both required so that the logoutd scripts that
  adhere to this API can safely rely on both being present. The logout cookbook is already passing both parameters
  anyway.

Miscellanea
"""""""""""

* idm: fix typo in docstring.

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

.. _`Thanos#Global_view`: https://wikitech.wikimedia.org/wiki/Thanos#Global_view

.. _`T257905`: https://phabricator.wikimedia.org/T257905
.. _`T283242`: https://phabricator.wikimedia.org/T283242
.. _`T327408`: https://phabricator.wikimedia.org/T327408

.. _`v0.0.1`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.1
.. _`v0.0.2`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.2
.. _`v0.0.3`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.3
.. _`v0.0.4`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.4
.. _`v0.0.5`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.5
.. _`v0.0.6`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.6
.. _`v0.0.7`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.7
.. _`v0.0.8`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.8
.. _`v0.0.9`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.9
.. _`v1.0.0`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.0.0
.. _`v1.0.1`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.0.1
.. _`v1.0.2`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.0.2
.. _`v1.1.0`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.1.0
.. _`v1.1.1`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.1.1
.. _`v1.1.2`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.1.2
.. _`v1.2.0`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.0
.. _`v1.2.1`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.1
.. _`v1.2.2`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.2
.. _`v1.2.3`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.3
.. _`v1.2.4`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.4
.. _`v1.2.5`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.5
.. _`v1.2.6`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v1.2.6
