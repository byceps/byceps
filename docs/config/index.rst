*************
Configuration
*************

BYCEPS can be configured with a configuration file. Some values can also
be set as environment variables.


Supported Configuration Values
==============================

.. py:data:: API_ENABLED

    Enable the REST API.

    Default: ``True``

.. py:data:: DEBUG

    Enable debug mode.

    Default: ``False``

    Handled by Flask_.

    Debug mode can also be enabled by appending the ``--debug`` option
    to the ``flask`` command.

.. py:data:: DEBUG_TOOLBAR_ENABLED

    Enable the debug toolbar (provided by Flask-DebugToolbar_).

    Default: ``False``

    .. _Flask-DebugToolbar: https://github.com/pallets-eco/flask-debugtoolbar

.. py:data:: JOBS_ASYNC

    Makes jobs run asynchronously.

    Can be disabled to run jobs synchronously, but that is likely only
    useful for (and actually used for) testing.

    Default: ``True``

.. py:data:: LOCALE

    Specifies the default locale.

    Default: ``de`` (This will likely be changed to ``en`` at some point
    in the future.)

.. py:data:: MAIL_HOST

    The host of the SMTP server.

    Default: ``'localhost'``

.. py:data:: MAIL_PASSWORD

    The password to authenticate with against the SMTP server.

    Default: ``None``

.. py:data:: MAIL_PORT

    The port of the SMTP server.

    Default: ``25``

.. py:data:: MAIL_STARTTLS

    Put the SMTP connection in TLS (Transport Layer Security) mode.

    Default: ``False``

.. py:data:: MAIL_SUPPRESS_SEND

    Suppress sending of emails.

    Default: ``False``

.. py:data:: MAIL_USE_SSL

    Use SSL for the connection to the SMTP server.

    Default: ``False``

.. py:data:: MAIL_USERNAME

    The username to authenticate with against the SMTP server.

    Default: ``None``

.. py:data:: METRICS_ENABLED

    Enable the Prometheus_-compatible metrics endpoint at ``/metrics``.

    Default: ``False``

    .. _Prometheus: https://prometheus.io/

.. py:data:: PATH_DATA

    Filesystem path for static files (including uploads).

    Default: ``'./data'`` (relative to the BYCEPS root path)

.. py:data:: PROPAGATE_EXCEPTIONS

    Reraise exceptions instead of letting BYCEPS handle them.

    This is useful if an external service like Sentry_ should handle
    exceptions.

    .. _Sentry: https://sentry.io/

    Default: ``None``

    If not set, this is implicitly true if ``DEBUG`` or ``TESTING`` is
    enabled.

    Handled by Flask_.

.. py:data:: REDIS_URL

    The URL used to connect to Redis.

    The format can be one of these::

        redis://[[username]:[password]]@localhost:6379/0
        rediss://[[username]:[password]]@localhost:6379/0
        unix://[[username]:[password]]@/path/to/socket.sock?db=0

    To use the first database of a Redis instance running on localhost
    on its default port: ``redis://127.0.0.1:6379/0``

    The documentation for ``Redis.from_url`` provides `details on
    supported URL schemes and examples
    <https://redis.readthedocs.io/en/stable/connections.html#redis.Redis.from_url>`_.

.. py:data:: SECRET_KEY

    A secret key that will be for security features such as signing
    session cookies.

    Should be a long, random string.

    BYCEPS provides a command-line tool to securely :ref:`generate a
    secret key <Generate Secret Key>`.

.. py:data:: SESSION_COOKIE_SECURE

    Only send cookies marked as secure when an HTTPS connection is
    available.

    Logging in will fail if this is set to true and BYCEPS is accessed
    without TLS.

    This behavior can be disabled for development purposes without a
    TLS-terminating frontend to the BYCEPS application.

    Default: ``True`` (set by BYCEPS; `Flask's default
    <https://flask.palletsprojects.com/en/2.2.x/config/#SESSION_COOKIE_SECURE>`_
    is ``False``)

.. py:data:: SHOP_ORDER_EXPORT_TIMEZONE

    The timezone used for shop order exports.

    Default: ``'Europe/Berlin'``

.. py:data:: SQLALCHEMY_DATABASE_URI

    The URL used to connect to the relational database (i.e. PostgreSQL).

    Format::

        postgresql+psycopg2://USERNAME:PASSWORD@HOST/DATABASE

    Example (user ``byceps`` with password ``hunter2`` wants to connect
    to database ``byceps`` on the local host)::

        postgresql+psycopg2://byceps:hunter2@127.0.0.1/byceps

    Since BYCEPS uses psycopg2_ by default, the scheme has to be
    `postgresql+psycopg2`.

    .. _psycopg2: https://www.psycopg.org/

    For more info, see `Flask-SQLAlchemy's documentation on
    SQLALCHEMY_DATABASE_URI
    <https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/config/#flask_sqlalchemy.config.SQLALCHEMY_DATABASE_URI>`_.

.. py:data:: SQLALCHEMY_ECHO

    Enable echoing of issued SQL queries. Useful for development and debugging.

    Default: ``False``

.. py:data:: STYLE_GUIDE_ENABLED

    Enable BYCEPS' style guide, available at ``/style_guide/`` both in
    admin mode and site mode.

.. py:data:: TESTING

    Enable testing mode.

    Only relevant when executing tests.

    Default: ``False``

    Handled by Flask_.


.. _Flask: https://github.com/pallets/flask
