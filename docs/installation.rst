Installation
============


Requirements
------------

* Python_ 3.7 or higher
* PostgreSQL_ 11 or higher
* Redis_ 5.0 or higher
* Git_ (for downloading and updating BYCEPS, but not strictly for running it)

.. _Python: https://www.python.org/
.. _PostgreSQL: https://www.postgresql.org/
.. _Redis: https://redis.io/
.. _Git: https://git-scm.com/


Debian
------

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

    # aptitude install git postgresql python3 python3-dev python3-venv redis-server

Additional required packages should be suggested for installation by
the package manager.

Refer to the Debian documentation for further details.

.. _Debian Linux: https://www.debian.org/


BYCEPS
------

Grab a copy of BYCEPS itself. For now, the best way probably is to
clone the Git repository from GitHub:

.. code-block:: sh

    $ git clone https://github.com/byceps/byceps.git

A new directory, ``byceps``, should have been created.

This way, it should be easy to pull in future updates to BYCEPS using
Git. (And there currently are no release tarballs anyway.)


Virtual Environment
-------------------

The installation should happen in an isolated Python_ environment just
for BYCEPS so that its requirements don't clash with different versions
of the same libraries somewhere else in the system.

Python_ already comes with the necessary tools, namely virtualenv_ and
pip_.

.. _virtualenv: https://www.virtualenv.org/
.. _pip: https://www.pip-installer.org/

Change into the BYCEPS path and create a virtual environment (named
"venv") there:

.. code-block:: sh

    $ cd byceps
    $ python3 -m venv venv

Activate it (but don't change into its path):

.. code-block:: sh

    $ . ./venv/bin/activate

Note that the first dot is the `dot command`_, followed by a relative
file name (which is written as explicitly relative to the current path,
``./``).

Whenever you want to activate the virtual environment, make sure to do
that either in the path in which you have created it using the above
command, or adjust the path to reference it relatively (e.g.
``../../venv/bin/activate``) or absolutely (e.g.
``/var/www/byceps/venv/bin/activate``).

Make sure the correct version of Python is used:

.. code-block:: sh

    (venv)$ python -V
    Python 3.9.2

It's probably a good idea to update pip_ to the current version:

.. code-block:: sh

    (venv)$ pip install --upgrade pip

Install the Python depdendencies via pip_:

.. code-block:: sh

    (venv)$ pip install -r requirements.txt

Install BYCEPS in editable mode to make ``import byceps`` work in
scripts:

.. code-block:: sh

    (venv)$ pip install -e .

.. _dot command: https://en.wikipedia.org/wiki/Dot_(Unix)


Database
--------

There should already be a system user, likely ``postgres``.

Become root:

.. code-block:: sh

    $ su
    <enter root password>

Switch to the ``postgres`` user:

.. code-block:: sh

    # su postgres

Create a database user named ``byceps``:

.. code-block:: sh

    postgres@host$ createuser --echo --pwprompt byceps

You should be prompted to enter a password. Do that.

Create a copy of ``config/development-example.py``
(``config/development.py`` from here on) and, in the copy,
replace the example password in the value of ``SQLALCHEMY_DATABASE_URI``
with the one you just entered.

Create a schema, also named ``byceps``:

.. code-block:: sh

    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps byceps

To run the tests (optional), a dedicated user and database have to be
created:

.. code-block:: sh

    postgres@host$ createuser --echo --pwprompt byceps_test
    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps_test byceps_test

Connect to the database:

.. code-block:: sh

    $ psql

Load the ``pgcrypto`` extension (only necessary on PostgreSQL versions
before 13):

.. code-block:: psql

    postgres=# CREATE EXTENSION pgcrypto;

Ensure that the function ``gen_random_uuid()`` is available now:

.. code-block:: psql

    postgres=# select gen_random_uuid();

Expected result (the actual UUID hopefully is different!):

.. code-block:: psql

               gen_random_uuid
    --------------------------------------
     b30bd643-d592-44e2-a256-0e0e167ac762
    (1 row)


Database Tables
---------------

Scripts are provided to create and populate database tables. Change the
path to be able to call them:

.. code-block:: sh

   $ cd scripts

Create the necessary tables:

.. code-block:: sh

   $ BYCEPS_CONFIG=../config/development.py APP_MODE=admin ./create_database_tables.py
   Creating database tables ... done.

An initial set of authorization permissions and roles is provided as a
TOML file. Import it into the database:

.. code-block:: sh

   $ BYCEPS_CONFIG=../config/development.py ./import_permissions_and_roles.py data/permissions_and_roles.toml
   Imported 32 roles.

With the authorization data in place, create the initial user (which
will get all available roles assigned):

.. code-block:: sh

   $ BYCEPS_CONFIG=../config/development.py ./create_initial_admin_user.py
   Screen name: Flynn
   Email address: flynn@flynns-arcade.net
   Password:
   Creating user "Flynn" ... done.
   Enabling user "Flynn" ... done.
   Assigning 33 roles to user "Flynn" ... done.

Those roles allow the user to log in to the admin backend and make all
administrative functionality available.
