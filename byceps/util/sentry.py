"""
byceps.util.sentry
~~~~~~~~~~~~~~~~~~

Sentry_ integration

.. _Sentry: https://sentry.io/

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
import os

import sentry_sdk
import structlog


log = structlog.get_logger()


@dataclass(frozen=True)
class SentryAppConfig:
    dsn: str
    environment: str
    component: str
    app_mode: str
    site_id: str | None


def configure_sentry_from_env(component: str) -> None:
    """Initialize and configure the Sentry SDK based on the environment."""
    config = _get_sentry_app_config_from_env(component)
    if config is None:
        log.info('Sentry integration: disabled (no DSN configured)')
        return None

    configure_sentry(config)

    log.info(
        'Sentry integration: enabled',
        environment=config.environment,
        component=component,
        app_mode=config.app_mode,
        site_id=config.site_id,
    )


def _get_sentry_app_config_from_env(component: str) -> SentryAppConfig | None:
    """Attempt to obtain Sentry configuration from environment."""
    dsn = os.environ.get('SENTRY_DSN')
    if not dsn:
        return None

    environment = os.environ.get('SENTRY_ENV', default='prod')

    app_mode = os.environ.get('APP_MODE', 'base')

    if app_mode == 'site':
        site_id = os.environ.get('SITE_ID')
    else:
        site_id = None

    return SentryAppConfig(
        dsn=dsn,
        environment=environment,
        component=component,
        app_mode=app_mode,
        site_id=site_id,
    )


def configure_sentry(config: SentryAppConfig) -> None:
    """Initialize and configure the Sentry SDK."""
    sentry_sdk.init(
        dsn=config.dsn,
        environment=config.environment,
    )

    sentry_sdk.set_tag('component', config.component)
    sentry_sdk.set_tag('app_mode', config.app_mode)

    if config.app_mode == 'site':
        sentry_sdk.set_tag('site_id', config.site_id)
