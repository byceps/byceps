Site Application
================

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

To run a site application with Flask's (insecure!) *development* server
for development purposes on a different port (to avoid conflicting with
the admin application):

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.py APP_MODE=site SITE_ID=cozylan FLASK_ENV=development flask run --debugger --reload --port 5001

The application for site ``cozylan`` should now be reachable at
`<http://127.0.0.1:5001>`_.

For now, every site will need its own site application instance.
