"""
byceps.config.converter
~~~~~~~~~~~~~~~~~~~~~~~

Configuration converter

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from typing import Any

from .models import BycepsConfig, DatabaseConfig


def convert_config(config: BycepsConfig) -> dict[str, Any]:
    """Convert configuration to dictionary accepted by Flask."""
    return dict(_generate_entries(config))


def _generate_entries(config: BycepsConfig) -> Iterator[tuple[str, Any]]:
    yield 'DEBUG', config.debug.enabled
    yield 'DEBUG_TOOLBAR_ENABLED', config.debug.toolbar_enabled

    yield 'LOCALE', config.locale

    timezone = config.timezone
    yield 'SHOP_ORDER_EXPORT_TIMEZONE', timezone
    yield 'TIMEZONE', timezone

    yield 'JOBS_ASYNC', config.jobs.asynchronous

    yield 'MAIL_HOST', config.smtp.host
    yield 'MAIL_PASSWORD', config.smtp.password
    yield 'MAIL_PORT', config.smtp.port
    yield 'MAIL_STARTTLS', config.smtp.starttls
    yield 'MAIL_SUPPRESS_SEND', config.smtp.suppress_send
    yield 'MAIL_USE_SSL', config.smtp.use_ssl
    yield 'MAIL_USERNAME', config.smtp.username

    yield 'METRICS_ENABLED', config.metrics.enabled

    yield 'PROPAGATE_EXCEPTIONS', config.propagate_exceptions

    yield 'REDIS_URL', config.redis.url

    yield 'SECRET_KEY', config.secret_key

    yield 'SQLALCHEMY_DATABASE_URI', _build_database_url(config.database)

    yield 'STYLE_GUIDE_ENABLED', config.styleguide.enabled


def _build_database_url(db_config: DatabaseConfig) -> str:
    """Assemble SQLAlchemy database URL."""
    scheme = 'postgresql+psycopg'
    return f'{scheme}://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}'
