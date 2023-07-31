**************
Running BYCEPS
**************

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.


Admin Application
=================

To run the admin application with Flask's (insecure!) *development*
server for development purposes:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.toml flask --app=serve_admin --debug run

The admin application should now be reachable at
`<http://127.0.0.1:5000>`_ (on Flask's standard port).


Site Application
================

To run a site application with Flask's (insecure!) *development* server
for development purposes on a different port (to avoid conflicting with
the admin application):

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.toml SITE_ID=cozylan flask --app=serve_site --debug run --port 5001

The application for site ``cozylan`` should now be reachable at
`<http://127.0.0.1:5001>`_.

For now, every site will need its own site application instance.


Worker
======

The worker processes background jobs for the admin application and site
applications.

To start it:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.toml ./worker.py

It should start processing any jobs in the queue right away and will
then wait for new jobs to be enqueued.

While technically multiple workers could be employed, a single one is
usually sufficient.
