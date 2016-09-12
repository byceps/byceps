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

Since 2014 BYCEPS is the foundation of the public website and local
party intranet of the LANresort_ event series.


.. _LANresort: https://www.lanresort.de/


:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
:Website: http://homework.nwsnet.de/releases/b1ce/#byceps


Installation
============

See ``docs/installation.rst``.


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
