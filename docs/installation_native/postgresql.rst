Prepare PostgreSQL
==================

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

In your :doc:`BYCEPS configuration file <byceps-config-file>`, replace
the example password in the value of ``SQLALCHEMY_DATABASE_URI`` with
the one you just entered.

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
