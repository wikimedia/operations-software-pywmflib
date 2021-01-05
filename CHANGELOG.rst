wmflib Changelog
----------------

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

.. _`v0.0.1`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.1
.. _`v0.0.2`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.2
.. _`v0.0.3`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.3
.. _`v0.0.4`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.4
.. _`v0.0.5`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.5
.. _`v0.0.6`: https://github.com/wikimedia/operations-software-pywmflib/releases/tag/v0.0.6
