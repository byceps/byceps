Create BYCEPS Configuration File
================================

To run BYCEPS, a configuration file is required. It usually resides in
:file:`config/`.

There is an example, :file:`config.toml.example`, that you can use as a
basis for your specific configuration.

Create a copy of the it to adjust as we go along:

.. code-block:: console

    $ cp config/config.toml.example config/config.toml


Set a Secret Key
----------------

A secret key is, among other things, required for login sessions. So
let's generate one in a cryptographically secure way:

.. code-block:: console

    $ uv run byceps generate-secret-key

Exemplary output:

.. code-block:: none

    3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293

Set this value in your configuration file so the line looks like this:

.. code-block:: toml
    :caption: excerpt from :file:`config/config.toml`

    secret_key = "3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293"

Note: This line has to be in the top part of the configuration file,
before any section (``[…]``).

.. attention:: Do **not** use the above key (or any other key you copied
   from anywhere). Generate **your own** secret key!

.. attention:: Do **not** use the same key for development and
   production environments. Generate **separate** secret keys!



Map Applications
----------------

Since a single BYCEPS instance can provide the admin frontend, the API,
*and* one or more sites, a mapping (in the ``[apps]`` section in the
configuration file) is required which defines which hostname will be
routed to which application.

- For a **local installation**, you can go with the exemplary hostnames
  already defined in the example configuration file, which are:

  - ``admin.byceps.example`` for the admin UI
  - ``api.byceps.example`` for the API
  - ``cozylan.example`` for the CozyLAN demo site

  To be able to access them, add these entries to your local
  :file:`/etc/hosts` file (or whatever the equivalent is for your
  operating system):

  .. code-block::
      :caption: excerpt from :file:`/etc/hosts`

      127.0.0.1       admin.byceps.example
      127.0.0.1       api.byceps.example
      127.0.0.1       cozylan.example

- But if you are **installing to a server on the Internet**, substitute
  above hostnames in the configuration with ones that use actual,
  registered Internet domains.


Specify SMTP Server
-------------------

BYCEPS needs to know of an SMTP server, or mail/message transport agent
(MTA), to forward outgoing emails to.

The default is to expect a local one on ``localhost`` and port 25
without authentication or encryption, like Sendmail_ or Postfix_.

Another option is to use an external one (authentication and encryption
are important here!) with a configuration like this:

.. code-block:: toml
    :caption: excerpt from :file:`config/config.toml`

    [smtp]
    host = "smtp.provider.example"
    port = 465
    use_ssl = true
    username = "smtp-user"
    password = "smtp-password"

See the available :ref:`SMTP configuration properties <SMTP Section>`.

.. _Sendmail: https://www.proofpoint.com/us/products/email-protection/open-source-email-solution
.. _Postfix: https://www.postfix.org/


Set Environment Variable Automatically
--------------------------------------

The configuration file has to be specified when running most commands.
This can be done by prefixing a command with the corresponding
environment variable:

.. code-block:: console

    $ BYCEPS_CONFIG_FILE=config/config.toml uv run byceps

To avoid doing that everytime, the environment variable can be saved to
the :file:`.env` file in the BYCEPS project path. For example:

.. code-block:: console

    $ echo "BYCEPS_CONFIG_FILE=$PWD/config/config.toml" > ./.env

Be sure to use an absolute path so that the file can be found even when
running commands from a sub-directory of the BYCEPS project path.
