Create BYCEPS Configuration File
================================

To run BYCEPS, a configuration file is required. Those usually reside in
:file:`config/`.

There are two examples, :file:`config.toml.example-development` and
:file:`config.toml.example-production`, that you can use as a base for
your specific configuration.

For starters, create a copy of the development example file to adjust as
we go along:

.. code-block:: console

    $ cp config/config.toml.example-development config/config.toml


Set a Secret Key
----------------

A secret key is, among other things, required for login sessions. So
let's generate one in a cryptographically secure way:

.. code-block:: console

    (.venv)$ byceps generate-secret-key

Exemplary output:

.. code-block:: none

    3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293

Set this value in your configuration file so the line looks like this:

.. code-block:: toml

    SECRET_KEY = "3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293"

.. attention:: Do **not** use the above key (or any other key you copied
   from anywhere). Generate **your own** secret key!

.. attention:: Do **not** use the same key for development and
   production environments. Generate **separate** secret keys!


Specify SMTP Server
-------------------

BYCEPS needs to know of an SMTP server, or mail/message transport agent
(MTA), to forward outgoing emails to.

The default is to expect a local one on ``localhost`` and port 25
without authentication or encryption, like Sendmail_ or Postfix_.

Another option is to use an external one (authentication and encryption
are important here!) with a configuration like this:

.. code-block:: toml

    MAIL_HOST = "smtp.provider.example"
    MAIL_PORT = 465
    MAIL_USE_SSL = true
    MAIL_USERNAME = "example-username"
    MAIL_PASSWORD = "example-password"

See the available ``MAIL_*`` configuration properties
(:confval:`MAIL_HOST`, etc.).

.. _Sendmail: https://www.proofpoint.com/us/products/email-protection/open-source-email-solution
.. _Postfix: https://www.postfix.org/
