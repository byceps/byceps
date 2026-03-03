"""
byceps.util.sentry
~~~~~~~~~~~~~~~~~~

Sentry_ integration

.. _Sentry: https://sentry.io/

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
import os

import sentry_sdk
import structlog


log = structlog.get_logger()


@dataclass(frozen=True, kw_only=True)
class SentryAppConfig:
    dsn: str
    environment: str
    component: str


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
    )


def _get_sentry_app_config_from_env(component: str) -> SentryAppConfig | None:
    """Attempt to obtain Sentry configuration from environment."""
    dsn = os.environ.get('SENTRY_DSN')
    if not dsn:
        return None

    environment = os.environ.get('SENTRY_ENV', default='prod')

    return SentryAppConfig(
        dsn=dsn,
        environment=environment,
        component=component,
    )


def configure_sentry(config: SentryAppConfig) -> None:
    """Initialize and configure the Sentry SDK."""
    sentry_sdk.init(
        dsn=config.dsn,
        environment=config.environment,
    )

    sentry_sdk.set_tag('component', config.component)
