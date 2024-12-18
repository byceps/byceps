*************
Configuration
*************

BYCEPS can be configured with a configuration file. Some values can also
be set as environment variables.


Supported Configuration Values
==============================

.. confval:: DEBUG
   :type: boolean
   :default: ``False``

   Enable debug mode.

   Handled by Flask_.

   Debug mode can also be enabled by appending the ``--debug`` option to
   the ``flask`` command.


.. confval:: DEBUG_TOOLBAR_ENABLED
   :type: boolean
   :default: ``False``

   Enable the debug toolbar (provided by Flask-DebugToolbar_).

   .. _Flask-DebugToolbar: https://github.com/pallets-eco/flask-debugtoolbar


.. confval:: JOBS_ASYNC
   :type: boolean
   :default: ``True``

   Make jobs run asynchronously.

   Can be disabled to run jobs synchronously, but that is likely only
   useful for (and actually used for) testing.


.. confval:: LOCALE
   :type: string

   The default locale.


.. confval:: MAIL_HOST
   :type: string
   :default: ``'localhost'``

   The host of the SMTP server.


.. confval:: MAIL_PASSWORD
   :type: string
   :default: ``None``

   The password to authenticate with against the SMTP server.


.. confval:: MAIL_PORT
   :type: integer
   :default: ``25``

   The port of the SMTP server.


.. confval:: MAIL_STARTTLS
   :type: boolean
   :default: ``False``

   Put the SMTP connection in TLS (Transport Layer Security) mode.


.. confval:: MAIL_SUPPRESS_SEND
   :type: boolean
   :default: ``False``

   Suppress sending of emails.


.. confval:: MAIL_USE_SSL
   :type: boolean
   :default: ``False``

   Use SSL for the connection to the SMTP server.


.. confval:: MAIL_USERNAME
   :type: string
   :default: ``None``

   The username to authenticate with against the SMTP server.


.. confval:: METRICS_ENABLED
   :type: boolean
   :default: ``False``

   Enable the Prometheus_-compatible metrics endpoint at ``/metrics/``.

   Only available on admin application.

   .. _Prometheus: https://prometheus.io/


.. confval:: PATH_DATA
   :type: path object
   :default: ``'./data'`` (relative to the BYCEPS root path)

   Filesystem path for static files (including uploads).


.. confval:: PAYPAL_CLIENT_ID
   :type: string

   The client ID for payments via PayPal.


.. confval:: PAYPAL_CLIENT_SECRET
   :type: string

   The client secret for payments via PayPal.


.. confval:: PAYPAL_ENVIRONMENT
   :type: string
   :default: ``sandbox``

   The environment for payments via PayPal.

   ``sandbox`` for testing, ``live`` for production use.


.. confval:: PROPAGATE_EXCEPTIONS
   :type: boolean
   :default: ``None``

   Reraise exceptions instead of letting BYCEPS handle them.

   This is useful if an external service like Sentry_ should handle
   exceptions.

   .. _Sentry: https://sentry.io/

   If not set, this is implicitly true if :confval:`DEBUG` or
   :confval:`TESTING` is enabled.

   Handled by Flask_.


.. confval:: REDIS_URL
   :type: string

   The URL used to connect to Redis.

   The format can be one of these:

   * ``redis://[[username]:[password]]@localhost:6379/0`` (TCP socket)
   * ``rediss://[[username]:[password]]@localhost:6379/0`` (SSL-wrapped
     TCP socket)
   * ``unix://[[username]:[password]]@/path/to/socket.sock?db=0`` (Unix
     domain socket)

   To use the first database of a Redis instance running on localhost
   on its default port: ``redis://127.0.0.1:6379/0``

   The documentation for ``Redis.from_url`` provides `details on
   supported URL schemes and examples
   <https://redis.readthedocs.io/en/stable/connections.html#redis.Redis.from_url>`_.


.. confval:: SECRET_KEY
   :type: string

   A secret key that will be for security features such as signing
   session cookies.

   Should be a long, random string.

   BYCEPS provides a command-line tool to securely :ref:`generate a
   secret key <Generate Secret Key>`.


.. confval:: SESSION_COOKIE_SECURE
   :type: boolean
   :default: ``True``

   Only send cookies marked as secure when an HTTPS connection is
   available.

   Logging in will fail if this is set to true and BYCEPS is accessed
   without TLS.

   This behavior can be disabled for development purposes without a
   TLS-terminating frontend to the BYCEPS application.

   The default value of ``True`` is set by BYCEPS. `Flask's default
   <https://flask.palletsprojects.com/en/2.2.x/config/#SESSION_COOKIE_SECURE>`_
   is ``False``.


.. confval:: SQLALCHEMY_DATABASE_URI
   :type: string

   The URL used to connect to the relational database (i.e. PostgreSQL).

   Format::

       postgresql+psycopg://USERNAME:PASSWORD@HOST/DATABASE

   Example (use user ``byceps`` with password ``hunter2`` to connect to
   database ``byceps`` on the local host)::

       postgresql+psycopg://byceps:hunter2@127.0.0.1/byceps

   Since BYCEPS uses psycopg_ by default, the scheme has to be
   `postgresql+psycopg`.

   .. _psycopg: https://www.psycopg.org/

   For more info, see `Flask-SQLAlchemy's documentation on
   SQLALCHEMY_DATABASE_URI
   <https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/config/#flask_sqlalchemy.config.SQLALCHEMY_DATABASE_URI>`_.


.. confval:: SQLALCHEMY_ECHO
   :type: boolean
   :default: ``False``

   Enable echoing of issued SQL queries. Useful for development and debugging.


.. confval:: STRIPE_PUBLISHABLE_KEY
   :type: string

   The publishable key for payments via Stripe.


.. confval:: STRIPE_SECRET_KEY
   :type: string

   The secret key for payments via Stripe.


.. confval:: STRIPE_WEBHOOK_SECRET
   :type: string

   The webhook secret for payments via Stripe.


.. confval:: STYLE_GUIDE_ENABLED
   :type: boolean
   :default: ``False``

   Enable BYCEPS' style guide, available at ``/style_guide/`` both in
   admin mode and site mode.


.. confval:: TESTING
   :type: boolean
   :default: ``False``

   Enable testing mode.

   Only relevant when executing tests.

   Handled by Flask_.


.. confval:: TIMEZONE
   :type: string

   The default timezone.


.. _Flask: https://github.com/pallets/flask
