Installation
============

Debian package
--------------

Wmflib is distributed as a Debian binary package ``python3-wmflib`` from `apt.wikimedia.org`_. The source package name
is ``python-wmflib``. It is built only for Debian Buster and newer Debian versions.

PyPI
----

Wmflib is available on `PyPI`_ and can be installed within a virtual environment with:

.. code-block:: none

    pip install wmflib

Source code
-----------

A gzipped tar archive of the source code for each release is available for download on the `Release page`_ on GitHub,
along with its GPG signature. The source code repository is available from `Wikimedia's Gerrit`_ website and mirrored
on `GitHub`_. To install it, from the ``master`` branch run:

.. code-block:: none

    python setup.py install

.. _`apt.wikimedia.org`: https://wikitech.wikimedia.org/wiki/APT_repository
.. _`PyPI`: https://pypi.org/project/wmflib/
.. _`Wikimedia's Gerrit`: https://gerrit.wikimedia.org/r/admin/repos/operations/software/pywmflib
.. _`GitHub`: https://github.com/wikimedia/operations-software-pywmflib
.. _`Release page`: https://github.com/wikimedia/operations-software-pywmflib/releases

