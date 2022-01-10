Create Database Tables
======================

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

Scripts are provided to create and populate database tables. Change the
path to be able to call them:

.. code-block:: sh

   (venv)$ cd scripts

Create the necessary tables:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py ./create_database_tables.py
   Creating database tables ... done.

An initial set of authorization permissions and roles is provided as a
TOML file. Import it into the database:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py ./import_permissions_and_roles.py data/permissions_and_roles.toml
   Imported 32 roles.

With the authorization data in place, create the initial user (which
will get all available roles assigned):

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py ./create_initial_admin_user.py
   Screen name: Flynn
   Email address: flynn@flynns-arcade.net
   Password:
   Creating user "Flynn" ... done.
   Enabling user "Flynn" ... done.
   Assigning 33 roles to user "Flynn" ... done.

Those roles allow the user to log in to the admin backend and make all
administrative functionality available.
