Install Debian Packages
=======================

`Debian Linux`_ is the recommended operating system to run BYCEPS on.

To install packages, become the ``root`` user (or prefix the following
commands with ``sudo`` to obtain superuser permissions):

.. code-block:: sh

    $ su -

Update the list of packages before installing any:

.. code-block:: sh

    # aptitude update

On Debian "Bullseye" 11 or Debian "Buster" 10, install these packages:

.. code-block:: sh

    # aptitude install git nginx postgresql python3 python3-dev python3-venv redis-server

Additional required packages should be suggested for installation by
the package manager.

Refer to the Debian documentation for further details.

.. _Debian Linux: https://www.debian.org/
