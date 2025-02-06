******************
Configuration File
******************

BYCEPS is meant to be configured with a configuration file.

An example file is available at :file:`config/config.toml.example`.


Top-Level Section
=================

.. code-block:: toml

    locale = "en"
    propagate_exceptions = false
    secret_key = "INDIVIDUAL-KEY-GOES-HERE"
    timezone = "Europe/Berlin"


.. confval:: locale
   :type: string

   The default locale.

   *required*


.. confval:: propagate_exceptions
   :type: boolean
   :default: ``false``

   Reraise exceptions instead of letting BYCEPS handle them.

   This is useful if an external service like Sentry_ should handle
   exceptions.

   If not set, this is implicitly true if debug mode and/or testing mode
   are enabled.

   Handled by Flask_.

   .. _Flask: https://github.com/pallets/flask
   .. _Sentry: https://sentry.io/

   *optional*


.. confval:: secret_key
   :type: string

   A secret key that will be for security features such as signing
   session cookies.

   Should be a long, random string.

   BYCEPS provides a command-line tool to securely :ref:`generate a
   secret key <Generate Secret Key>`.

   *required*


.. confval:: timezone
   :type: string

   The default timezone.

   *required*


Applications Section
====================

Maps applications to hostnames.

At least one application has to be specified.

An example with admin application, API application, and two sites:

.. code-block:: toml

    [apps]
    admin = { server_name = "admin.example" }
    api = { server_name = "api.example" }
    sites = [
      { server_name = "site1.example", site_id = "site1" },
      { server_name = "site2.example", site_id = "site2" },
    ]


.. confval:: apps.admin
   :type: string

   Hostname to mount the admin application on.

   *optional*


.. confval:: apps.api
   :type: string

   Hostname to mount the API application on.

   *optional*


.. confval:: apps.sites
   :type: string

   Hostnames to mount site applications on.

   *optional*


Database Section
================

Properties to connect to the relational database (i.e. PostgreSQL) with.

An example that connects to PostgreSQL on the local host and the default
port, authenticating as user ``byceps`` with password ``hunter2``, and
selecting the named database ``byceps``:

.. code-block:: toml

    [database]
    host = "localhost"
    port = 5432
    username = "byceps"
    password = "hunter2"
    database = "byceps"


.. confval:: database.host
   :type: string
   :default: ``"localhost"``

   Hostname to connect to.

   *optional*


.. confval:: database.port
   :type: int
   :default: ``5432``

   Port to connect to.

   *optional*


.. confval:: database.username
   :type: string

   Username to authenticate with.

   *required*


.. confval:: database.password
   :type: string

   Password to authenticate with.

   *required*


.. confval:: database.database
   :type: string

   Database to use.

   *required*


Development Section
===================

Development helpers

An example that enables the style guide but not the debug toolbar:

.. code-block:: toml

    [development]
    style_guide_enabled = true
    toolbar_enabled = false


.. confval:: development.style_guide_enabled
   :type: boolean
   :default: ``false``

   Enables BYCEPS' style guide, available at ``/style_guide/`` both in
   admin mode and site mode.

   *optional*


.. confval:: development.toolbar_enabled
   :type: boolean
   :default: ``false``

   Enables the debug toolbar (provided by Flask-DebugToolbar_).

   .. _Flask-DebugToolbar: https://github.com/pallets-eco/flask-debugtoolbar

   *optional*


Discord Section
===============

Integration with Discord_.

.. _Discord: https://discord.com/


.. code-block:: toml

    [discord]
    enabled = true
    client_id = "discord-client-id"
    client_secret = "discord-client-secret"


.. confval:: discord.enabled
   :type: boolean
   :default: ``false``

   Enables the integration Discord.

   *required if section is defined*


.. confval:: discord.client_id
   :type: string

   Discord client ID.

   *required if section is defined*


.. confval:: discord.client_secret
   :type: string

   Discord client secret.

   *required if section is defined*


Invoice Ninja Section
=====================

Integration with `Invoice Ninja`_.

.. _Invoice Ninja: https://invoiceninja.com/


.. code-block:: toml

    [invoiceninja]
    enabled = true
    api_key = "random-characters"
    base_url = "https://invoiceninja.example"


.. confval:: invoiceninja.enabled
   :type: boolean
   :default: ``false``

   Enables the integration with Invoice Ninja.

   *required if section is defined*


.. confval:: invoiceninja.api_key
   :type: string

   Invoice Ninja API key.

   *required if section is defined*


.. confval:: invoiceninja.base_url
   :type: string

   Base URL (without trailing slash) of the Invoice Ninja instance to
   integrate with.

   *required if section is defined*


Metrics Section
===============

Enable the Prometheus_-compatible metrics endpoint at ``/metrics/``.

Only available on the admin application.

.. _Prometheus: https://prometheus.io/


An example that enables the metrics endpoint:

.. code-block:: toml

    [metrics]
    enabled = true


.. confval:: metrics.enabled

   :type: boolean
   :default: ``false``

   Enables the metrics endpoint.

   *required if section is defined*


Payment Gateways Section
========================

Payment gateway integrations


PayPal Section
--------------

Integration with payment gateway provider PayPal_.

.. _PayPal: https://www.paypal.com/


.. code-block:: toml

    [payment_gateways.paypal]
    enabled = true
    client_id = "paypal-client-id"
    client_secret = "paypal-client-secret"
    environment = "sandbox"


.. confval:: payment_gateways.paypal.client_id
   :type: string

   The client ID for payments via PayPal.

   *required if section is defined*


.. confval:: payment_gateways.paypal.client_secret
   :type: string

   The client secret for payments via PayPal.

   *required if section is defined*


.. confval:: payment_gateways.paypal.environment
   :type: string

   The environment for payments via PayPal.

   ``sandbox`` for testing, ``live`` for production use.

   *required if section is defined*


Stripe Section
--------------

Integration with payment gateway provider Stripe_.

.. _Stripe: https://stripe.com/


.. code-block:: toml

    [payment_gateways.stripe]
    enabled = true
    secret_key = "stripe-secret-key"
    publishable_key = "stripe-publishable-key"
    webhook_secret = "stripe-webhook-secret"


.. confval:: payment_gateways.stripe.publishable_key
   :type: string

   The publishable key for payments via Stripe.

   *required if section is defined*


.. confval:: payment_gateways.stripe.secret_key
   :type: string

   The secret key for payments via Stripe.

   *required if section is defined*


.. confval:: payment_gateways.stripe.webhook_secret
   :type: string

   The webhook secret for payments via Stripe.

   *required if section is defined*


Redis Section
=============

URL to connect to the Redis_ database with.

.. _Redis: https://redis.io/


An example for a Redis instance running on the local host on its default
port, using the first database (#0):

.. code-block:: toml

    [redis]
    url = "redis://127.0.0.1:6379/0"


.. confval:: redis.url
   :type: string

   The URL used to connect to Redis.

   The format can be one of these:

   * ``redis://[[username]:[password]]@localhost:6379/0`` (TCP socket)
   * ``rediss://[[username]:[password]]@localhost:6379/0`` (SSL-wrapped
     TCP socket)
   * ``unix://[[username]:[password]]@/path/to/socket.sock?db=0`` (Unix
     domain socket)

   The documentation for ``Redis.from_url`` provides `details on
   supported URL schemes and examples
   <https://redis.readthedocs.io/en/stable/connections.html#redis.Redis.from_url>`_.

   *required*


SMTP Section
============

E-mail sending via the Simple Mail Transfer Protocol (SMTP).

An example to send e-mail to a mail server on the local host on its
standard port:

.. code-block:: toml

    [smtp]
    host = "localhost"
    port = 25
    starttls = true
    use_ssl = true
    username = "smtp-user"
    password = "smtp-password"
    suppress_send = false


.. confval:: smtp.host
   :type: string
   :default: ``"localhost"``

   The host of the SMTP server.

   *optional*


.. confval:: smtp.password
   :type: string
   :default: ``""``

   The password to authenticate with against the SMTP server.

   *optional*


.. confval:: smtp.port
   :type: integer
   :default: ``25``

   The port of the SMTP server.

   *optional*


.. confval:: smtp.starttls
   :type: boolean
   :default: ``false``

   Put the SMTP connection in TLS (Transport Layer Security) mode.

   *optional*


.. confval:: smtp.suppress_send
   :type: boolean
   :default: ``false``

   Suppress sending of e-mails.

   *optional*


.. confval:: smtp.use_ssl
   :type: boolean
   :default: ``false``

   Use SSL for the connection to the SMTP server.

   *optional*


.. confval:: smtp.username
   :type: string
   :default: ``""``

   The username to authenticate with against the SMTP server.

   *optional*
