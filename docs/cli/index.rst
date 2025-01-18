**********************
Command-line Interface
**********************

BYCEPS comes with a command-line tool for some tasks.

.. important:: Before attempting to run any ``byceps`` command, make
   sure that the :doc:`virtual environment
   </installation_native/virtual-env>` is set up and activated.

.. list-table::
   :header-rows: 1

   * - Command
     - Description
   * - ``byceps create-database-tables``
     - :ref:`Create database tables <Create Database Tables>`
   * - ``byceps create-superuser``
     - :ref:`Create superuser <Create Superuser>`
   * - ``byceps export-roles``
     - :ref:`Export authorization roles <Export Authorization Roles>`
   * - ``byceps generate-secret-key``
     - :ref:`Generate secret key <Generate Secret Key>`
   * - ``byceps import-roles``
     - :ref:`Import authorization roles <Import Authorization Roles>`
   * - ``byceps import-seats``
     - :ref:`Import seats <Import Seats>`
   * - ``byceps import-users``
     - :ref:`Import users <Import Users>`
   * - ``byceps initialize-database``
     - :ref:`Initialize database <Initialize Database>`
   * - ``byceps shell``
     - :ref:`Run interactive shell <Run Interactive Shell>`


Create Database Tables
======================

``byceps create-database-tables`` creates the tables that are required
to run BYCEPS in a relational database instance.

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps create-database-tables

Expected output:

.. code-block:: none

    Creating database tables ... done.

.. note:: The :ref:`database initialization command <Initialize
   Database>` covers this command.


Import Authorization Roles
==========================

``byceps import-roles`` imports authorization roles from a file in TOML
format into BYCEPS.

By default, an initial set of roles provided with BYCEPS is imported:

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps import-roles

Expected output:

.. code-block:: none

    Importing roles ... done. Imported 35 roles, skipped 0 roles.

Optionally, the file to import from can be specified with the option
``-f``/``--file``:

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps import-roles -f custom_roles.toml

Expected output:

.. code-block:: none

    Importing roles ... done. Imported 35 roles, skipped 0 roles.

.. note:: The :ref:`database initialization command <Initialize
   Database>` covers this command (except for the option to provide a
   custom roles file).


Export Authorization Roles
==========================

``byceps export-roles`` exports authorization roles in TOML format from
BYCEPS to standard output.

To export all roles into a TOML file, standard output is redirected
(``>``) to it:

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps export-roles > exported-roles.toml


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

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps initialize-database

Expected output:

.. code-block:: none

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

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps create-superuser

Expected output:

.. code-block:: none

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

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps import-users example-users.jsonl

Expected output:

.. code-block:: none

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

    (.venv)$ byceps generate-secret-key

Expected output:

.. code-block:: none

    3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293

.. attention:: Do **not** use the above key (or any other key you copied
   from anywhere). Generate **your own** secret key!

.. attention:: Do **not** use the same key for development and
   production environments. Generate **separate** secret keys!


Import Seats
============

``byceps import-seats`` imports seats from a file in `JSON Lines`_
format into BYCEPS.

Currently supported fields:

- ``area_title`` (required)
- ``coord_x`` (required)
- ``coord_y`` (required)
- ``rotation``
- ``category_title`` (required)
- ``label``
- ``type_``

Example file:

.. code-block:: json

    {"area_title": "Floor 3", "coord_x": 10, "coord_y": 10, "rotation": 0, "category_title": "Premium", "label": "Seat A-1"}
    {"area_title": "Floor 3", "coord_x": 25, "coord_y": 10, "rotation": 0, "category_title": "Premium", "label": "Seat A-2"}

To import it:

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps import-seats my-party-2023 example-seats.jsonl

Expected output:

.. code-block:: none

    [line 1] Imported seat (area="Floor 3", x=10, y=10, category="Premium").
    [line 2] Imported seat (area="Floor 3", x=25, y=10, category="Premium").


.. _JSON Lines: https://jsonlines.org/


Run Interactive Shell
=====================

The BYCEPS shell is an interactive Python command line prompt that
provides access to BYCEPS' functionality as well as the persisted data.

This can be helpful to inspect and manipulate the application's data by
using primarily the various services (from ``byceps.services``) without
directly accessing the database (hopefully limiting the amount of
accidental damage).

.. code:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps shell

Expected output:

.. code-block:: none

    Welcome to the interactive BYCEPS shell on Python 3.11.2!
    >>>
