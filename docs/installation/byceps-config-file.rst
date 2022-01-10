Create BYCEPS Configuration File
================================

To run BYCEPS, a configuration file is required. Those usually reside in
``/config``.

There are two examples, ``development-example.py`` and
``production-example.py``, that you can use as a base for your specific
configuration.

For starters, create a copy of the development example file to adjust as
we go along:

.. code-block:: sh

    $ cp config/development-example.py config/development.py


Set a Secret Key
----------------

A secret key is, among other things, required for login sessions. So
let's generate one in a cryptographically secure way:

.. code-block:: sh

    (venv)$ python -c 'import secrets; print(secrets.token_hex())'
    3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293

Set this value in your configuration file so the line looks like this:

.. code-block:: py

    SECRET_KEY = '3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293'

.. attention:: Do **not** use the above key (or any other key you copied
   from anywhere). Generate your own secret key!

.. attention:: Do **not** use the same key for development and
   production environments. Generate separate secret keys!
