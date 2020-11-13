"""
byceps.util.sentry
~~~~~~~~~~~~~~~~~~

Sentry_ integration

.. _Sentry: https://sentry.io/

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask


def configure_sentry_for_webapp(dsn: str, environment: str, app: Flask) -> None:
    """Initialize and configure the Sentry SDK for the Flask-based web
    application (both in 'admin' and 'site' modes).
    """
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=dsn, environment=environment, integrations=[FlaskIntegration()],
    )

    app_mode = app.config.get('APP_MODE')
    sentry_sdk.set_tag('app_mode', app_mode)

    if app_mode == 'site':
        sentry_sdk.set_tag('site_id', app.config.get('SITE_ID'))


def configure_sentry_for_worker(dsn: str, environment: str) -> None:
    """Initialize and configure the Sentry SDK for the RQ worker."""
    import sentry_sdk
    from sentry_sdk.integrations.rq import RqIntegration

    sentry_sdk.init(
        dsn=dsn, environment=environment, integrations=[RqIntegration()],
    )

    sentry_sdk.set_tag('app_mode', 'worker')
