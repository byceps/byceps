*****
Shell
*****

The application shell is an interactive Python command line prompt that
provides access to BYCEPS' functionality as well as the persisted data.

This can be helpful to inspect and manipulate the system's data by using
primarily the various services (from ``byceps.services``) without
directly accessing the database (hopefully limiting the amount of
accidental damage).

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

.. code:: sh

    (venv)$ BYCEPS_CONFIG=../config/development.toml flask shell

Installation of an extra package makes the shell easier to use due to features
like command history and auto-completion:

.. code:: sh

    (venv)$ pip install flask-shell-ipython
