Populate Database
=================

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation_native/virtual-env>` is set up and
   activated.

Initialize the database (:ref:`details <Initialize Database>`) specified
in the configuration file:

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps initialize-database

Expected output:

.. code-block:: none

    Creating database tables ... done.
    Importing roles ... done. Imported 35 roles, skipped 0 roles.
    Adding language "en" ... done.
    Adding language "de" ... done.

With the tables and the authorization data in place, create the initial
user (which will get all available roles assigned):

.. code-block:: sh

    (.venv)$ BYCEPS_CONFIG=config/config.toml byceps create-superuser

Enter user account details interactively:

.. code-block:: none

    Screen name: Flynn
    Email address: flynn@flynns-arcade.net
    Password: hunter2

Expected output:

.. code-block:: none

    Creating user "Flynn" ... done.
    Enabling user "Flynn" ... done.
    Assigning 35 roles to user "Flynn" ... done.

Those roles allow the user to log in to the admin backend and to access
all administrative functionality.
