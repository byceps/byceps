Worker
======

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

The worker processes background jobs for the admin application and site
applications.

To start it:

.. code-block:: sh

   (venv)$ BYCEPS_CONFIG=../config/development.toml ./worker.py

It should start processing any jobs in the queue right away and will
then wait for new jobs to be enqueued.

While technically multiple workers could be employed, a single one is
usually sufficient.
