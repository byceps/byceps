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

In 2016 and 2017, respectively, `LANresort Bostalsee`_ and NorthCon_
have been (re-)launched on BYCEPS.


.. _LANresort: https://www.lanresort.de/
.. _LANresort Bostalsee: https://bostalsee.lanresort.de/
.. _NorthCon: https://www.northcon.de/


:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
:Website: http://homework.nwsnet.de/releases/b1ce/#byceps


Installation
============

See ``docs/installation.rst``.


Testing
=======

In the activated virtual environment, install tox_ and nose2_:

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

    $ BYCEPS_CONFIG=../config/development_admin.py ./manage.py runserver -p 8080

In a production environment, it is recommended to have the application
served by uWSGI_ or Gunicorn_.

It is furthermore recommended to run it locally behind nginx_ and have
the latter both serve static files and provide SSL encryption.


.. _uWSGI: http://uwsgi-docs.readthedocs.io/
.. _Gunicorn: http://gunicorn.org/
.. _nginx: http://nginx.org/
