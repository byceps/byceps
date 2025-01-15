**********
Run BYCEPS
**********

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation_native/virtual-env>` is set up and
   activated.


Applications
============

To run the applications defined in the :doc:`application mapping file
<apps-config-file>` with Flask's (insecure!) *development* server for
development purposes:

.. code-block:: sh

   (.venv)$ BYCEPS_CONFIG=config/development.toml BYCEPS_APPS_CONFIG=config/apps.toml flask --app=serve_apps --debug run

If the hostname mapping (or DNS setup) is also correct, the configured
BYCEPS applications should be accessible at their respective hostnames
on Flask's standard port (5000), for example:

- `<http://admin.byceps.example:5000/>`_
- `<http://api.byceps.example:5000/>`_
- `<http://cozylan.example:5000/>`_


Worker
======

The worker processes background jobs for the admin application and site
applications.

To start it:

.. code-block:: sh

   (.venv)$ BYCEPS_CONFIG=config/development.toml byceps worker

It should start processing any jobs in the queue right away and will
then wait for new jobs to be enqueued.

While technically multiple workers could be employed, a single one is
usually sufficient.
