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
