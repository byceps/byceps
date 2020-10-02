Installation
============


Requirements
------------

* Python_ 3.7 or higher
* PostgreSQL_ 9.6 or higher
* Redis_ 2.8 or higher
* Git_ (for downloading and updating BYCEPS, but not strictly for running it)

.. _Python: https://www.python.org/
.. _PostgreSQL: https://www.postgresql.org/
.. _Redis: https://redis.io/
.. _Git: https://git-scm.com/


Debian
------

`Debian Linux`_ is the recommended operating system to run BYCEPS on.

The following packages are available as part of the current (as of
August 2019) Debian "Buster" release:

* ``git``
* ``postgresql-11``
* ``python3.7``
* ``python3.7-dev``
* ``python3.7-venv``
* ``redis-server``

Additional required packages should be suggested for installation by
the package manager.

Update the package list and install the necessary packages (as the root
user):

.. code-block:: sh

    # aptitude update
    # aptitude install git postgresql-11 python3.7 python3.7-dev python3.7-venv redis-server

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
    $ python3.7 -m venv --system-site-packages venv

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
    Python 3.7.3

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

Create a copy of ``config/development_admin.py`` and, in the copy,
replace the example password in the value of
``SQLALCHEMY_DATABASE_URI`` with the one you just entered.

Create a schema, also named ``byceps``:

.. code-block:: sh

    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps byceps

To run the tests, a dedicated user and database have to be created:

.. code-block:: sh

    postgres@host$ createuser --echo --pwprompt byceps_test
    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps_test byceps_test

Connect to the database:

.. code-block:: sh

    $ psql

Load the ``pgcrypto`` extension:

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

   $ BYCEPS_CONFIG=../config/yourconfig.py ./create_database_tables.py
   Creating database tables ... done.

An initial set of authorization permissions and roles is provided as a
TOML file. Import it into the database:

.. code-block:: sh

   $ BYCEPS_CONFIG=../config/yourconfig.py ./import_permissions_and_roles.py data/permissions_and_roles.toml
   Importing 75 permissions ... done.
   Importing 29 roles ... done.

With the authorization data in place, create the initial user (which
will get all available roles assigned):

.. code-block:: sh

   $ BYCEPS_CONFIG=../config/yourconfig.py ./create_initial_admin_user.py
   Screen name: Flynn
   Email address: flynn@flynns-arcade.net
   Password:
   Creating user "Flynn" ... done.
   Enabling user "Flynn" ... done.
   Assigning 29 roles to user "Flynn" ... done.

Those roles allow the user to log in to the admin backend and make all
administrative functionality available.
