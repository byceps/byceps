Create Database Tables
======================

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

Create the tables in the database specified in the configuration file:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py byceps create-database-tables
   Creating database tables ... done.

An initial set of authorization roles is provided as a TOML file. Import
it into the database:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py byceps import-roles scripts/data/roles.toml
   Imported 32 roles.

With the authorization data in place, create the initial user (which
will get all available roles assigned):

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py byceps create-superuser
   Screen name: Flynn
   Email address: flynn@flynns-arcade.net
   Password:
   Creating user "Flynn" ... done.
   Enabling user "Flynn" ... done.
   Assigning 33 roles to user "Flynn" ... done.

Those roles allow the user to log in to the admin backend and to access
all administrative functionality.
