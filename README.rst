======
BYCEPS
======


BYCEPS is the Bring-Your-Computer Event Processing System.

It is a tool to prepare and operate a LAN party, both online on the
Internet and locally as an intranet system, for both organizers and
attendees.

The system incorporates both experience from more than 15 years of
organizing LAN parties as well as concepts and source code developed
for more than a decade.


Requirements
============

- Python_ 3.4.2 or higher
- PostgreSQL_ 9.4 or higher

.. _Python: http://www.python.org/
.. _PostgreSQL: http://www.postgresql.org/


Installation
============

The installation should happen in an isolated environment just for
BYCEPS so that its requirements don't clash with different versions of
the same libraries somewhere else in the system.

Python_ already comes with the necessary tools, namely virtualenv_ and
pip_.


.. _virtualenv: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org/


Debian
------

Debian_ Linux is the suggested operating system to run BYCEPS on.

The following packages available in the Debian repository as part of
the "Jessie" release:

- postgresql-9.4
- postgresql-contrib-9.4
- python3.4
- python3.4-dev  
- python3.4-venv

Additional required packages should be suggested for installation by
the package manager.

Update the package list and install the necessary packages (as the root
user):

.. code:: sh

    # aptitude update
    # aptitude install postgresql-9.4 postgresql-contrib-9.4 python3.4 python3.4-dev python3.4-venv

Refer to the Debian documentation for further details.


.. _Debian: https://www.debian.org/


Set up the virtual environment
------------------------------

Create a virtual environment (named "venv"):

.. code:: sh

    $ pyvenv venv

Activate it:

.. code:: sh

    $ . ./venv/bin/activate

Make sure the correct version of Python is used:

.. code:: sh

    (venv)$ python -V
    Python 3.4.2

Install the Python depdendencies via pip_:

.. code:: sh

    (venv)$ pip install -r requirements.txt


Configuration
=============


Database
--------

There should already be a system user, likely 'postgres'.

Become root:

.. code:: sh

    $ su
    <enter root password>

Switch to the 'postgres' user:

.. code:: sh

    # su postgres

Create a database user named 'byceps':

.. code:: sh

    postgres@host$ createuser --echo --pwprompt byceps

You should be prompted to enter a password. Do that.

Create a schema, also named 'byceps':

.. code:: sh

    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps byceps

Connect to the database:

.. code:: sh

    $ psql

Load the 'pgcrypto' extension:

.. code::

    postgres=# CREATE EXTENSION pgcrypto;

Ensure that the function 'gen_random_uuid()' is available now:

.. code::

    postgres=# select gen_random_uuid();

Expected result:

.. code::

               gen_random_uuid
    --------------------------------------
     b30bd643-d592-44e2-a256-0e0e167ac762
    (1 row)


Testing
=======

In the activate virtual environment, install tox_ and nose2_:

.. code:: sh

    (venv)$ pip install -r requirements-test.txt

Have tox run the tests:

.. code:: sh

    (venv)$ tox

If run for the first time, tox will first create virtual environments
for the Python versions specified in `tox.ini`.


.. _tox: http://tox.testrun.org/
.. _nose2: https://github.com/nose-devs/nose2


Serving
=======

To spin up a server (only for development purposes!) on port 8080 with
debugging middleware and in-browser code evaluation:

.. code:: sh

    $ ./manage.py runserver -p 8080

In a production environment, the Gunicorn_ server is highly recommended
to serve the Python application.

It is furthermore recommended to run it locally behind nginx_ and have
the latter both serve static files and provide SSL encryption.


.. _Gunicorn: http://gunicorn.org/
.. _nginx: http://nginx.org/
