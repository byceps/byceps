**********************
Command-line Interface
**********************

BYCEPS comes with a command-line tool for some tasks.

.. important:: Before attempting to run any ``byceps`` command, make
   sure that the :doc:`virtual environment </installation/virtual-env>`
   is set up and activated.

.. list-table::
   :header-rows: 1

   * - Command
     - Description
   * - ``byceps create-database-tables``
     - :ref:`Create Database Tables`
   * - ``byceps create-superuser``
     - :ref:`Create Superuser`
   * - ``byceps export-roles``
     - :ref:`Export Authorization Roles`
   * - ``byceps generate-secret-key``
     - :ref:`Generate Secret Key`
   * - ``byceps import-roles``
     - :ref:`Import Authorization Roles`
   * - ``byceps import-users``
     - :ref:`Import Users`
   * - ``byceps initialize-database``
     - :ref:`Initialize Database`


Create Database Tables
======================

``byceps create-database-tables`` creates the tables that are required
to run BYCEPS in a relational database instance.

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps create-database-tables
    Creating database tables ... done.

.. note:: :ref:`Initialize Database` covers this.


Import Authorization Roles
==========================

``byceps import-roles`` imports authorization roles from a file in TOML
format into BYCEPS.

By default, an initial set of roles provided with BYCEPS is imported:

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps import-roles
    Importing roles ... done. Imported 35 roles, skipped 0 roles.

Optionally, the file to import from can be specified with the option
``-f``/``--file``:

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps import-roles -f custom_roles.toml
    Importing roles ... done. Imported 35 roles, skipped 0 roles.

.. note:: :ref:`Initialize Database` covers this (except for the option
   to provide a custom roles file).


Export Authorization Roles
==========================

``byceps export-roles`` exports authorization roles in TOML format from
BYCEPS to standard output.

To export all roles into a TOML file, standard output is redirected
(``>``) to it:

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps export-roles > exported-roles.toml


Initialize Database
===================

``byceps initialize-database`` prepares a relational database instance
for running BYCEPS.

It is a convenience command that includes the following steps (making it
unnecessary to call the covered commands separately):

- Create the database tables. (What :ref:`Create Database Tables` does.)
- Import authorization roles. (What :ref:`Import Authorization Roles` does.)
- Register the supported languages.

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps initialize-database
    Creating database tables ... done.
    Importing roles ... done. Imported 35 roles, skipped 0 roles.
    Adding language "en" ... done.
    Adding language "de" ... done.


Create Superuser
================

``byceps create-superuser`` creates a BYCEPS superuser.

This will:

- create a user account,
- initialize the account,
- assign all existing authorization roles to the account, and
- confirm the associated email address as valid (even though it might
  not be).

This command is necessary to create the initial user account, which then
can be used to log in to the admin backend and to access all
administrative functionality.

The command can be run to create additional user accounts as well, but
they all will have superuser-like privileges in BYCEPS.

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps create-superuser
    Screen name: Flynn
    Email address: flynn@flynns-arcade.net
    Password:
    Creating user "Flynn" ... done.
    Enabling user "Flynn" ... done.
    Assigning 35 roles to user "Flynn" ... done.

.. note:: This command will only assign the roles that exist in the
   database. If no roles have been imported, none will be assigned.


Import Users
============

``byceps import-users`` imports basic user accounts from a file in `JSON
Lines`_ format into BYCEPS.

.. _JSON Lines: https://jsonlines.org/

This functionality exists to support migration from another system to
BYCEPS.

Currently supported fields:

- ``screen_name`` (required)
- ``email_address``
- ``legacy_id``
- ``first_name``, ``last_name``
- ``date_of_birth``
- ``country``, ``zip_code``, ``city``, ``street``
- ``phone_number``
- ``internal_comment``

Example file (including a deliberately bad record):

.. code-block:: json

    {"screen_name": "imported01", "email_address": "imported01@example.test", "first_name": "Alice", "last_name": "Allison"}
    {"bad": "data"}
    {"screen_name": "imported02", "email_address": "imported02@example.test", "first_name": "Bob", "last_name": "Bobson"}
    {"screen_name": "imported03"}

To import it:

.. code-block:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.py byceps import-users example-users.jsonl
    [line 1] Imported user imported01.
    [line 2] Could not import user: 1 validation error for UserToImport
    screen_name
      field required (type=value_error.missing)
    [line 3] Imported user imported02.
    [line 4] Imported user imported03.



Generate Secret Key
===================

``byceps generate-secret-key`` generates a secret key in a
cryptographically secure way.

A secret key is, among other things, required for login sessions.

.. code-block:: sh

    (venv)$ byceps generate-secret-key
    3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293

.. attention:: Do **not** use the above key (or any other key you copied
   from anywhere). Generate your own secret key!

.. attention:: Do **not** use the same key for development and
   production environments. Generate separate secret keys!
