"""
byceps.util.sentry
~~~~~~~~~~~~~~~~~~

Sentry_ integration

.. _Sentry: https://sentry.io/

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask


def configure_sentry_for_webapp(dsn: str, environment: str, app: Flask) -> None:
    """Initialize and configure the Sentry SDK for the Flask-based web
    application (both in 'admin' and 'site' modes).
    """
    sentry_sdk = _init_sentry_sdk(dsn, environment)

    app_mode = app.config.get('APP_MODE')
    sentry_sdk.set_tag('app_mode', app_mode)

    if app_mode == 'site':
        sentry_sdk.set_tag('site_id', app.config.get('SITE_ID'))


def configure_sentry_for_worker(dsn: str, environment: str) -> None:
    """Initialize and configure the Sentry SDK for the RQ worker."""
    sentry_sdk = _init_sentry_sdk(dsn, environment)

    sentry_sdk.set_tag('app_mode', 'worker')


def _init_sentry_sdk(dsn: str, environment: str):
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.rq import RqIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            FlaskIntegration(),
            RedisIntegration(),
            RqIntegration(),
            SqlalchemyIntegration(),
        ],
    )

    return sentry_sdk
