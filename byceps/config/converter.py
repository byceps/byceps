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
    yield 'PATH_DATA', config.data_path

    yield 'TESTING', config.testing

    yield 'LOCALE', config.locale

    timezone = config.timezone
    yield 'SHOP_ORDER_EXPORT_TIMEZONE', timezone
    yield 'TIMEZONE', timezone

    if (config.discord is not None) and config.discord.enabled:
        yield 'DISCORD_CLIENT_ID', config.discord.client_id
        yield 'DISCORD_CLIENT_SECRET', config.discord.client_secret

    yield 'JOBS_ASYNC', config.jobs.asynchronous

    yield 'MAIL_HOST', config.smtp.host
    yield 'MAIL_PASSWORD', config.smtp.password
    yield 'MAIL_PORT', config.smtp.port
    yield 'MAIL_STARTTLS', config.smtp.starttls
    yield 'MAIL_SUPPRESS_SEND', config.smtp.suppress_send
    yield 'MAIL_USE_SSL', config.smtp.use_ssl
    yield 'MAIL_USERNAME', config.smtp.username

    paypal_config = config.payment_gateways.paypal
    if paypal_config and paypal_config.enabled:
        yield 'PAYPAL_CLIENT_ID', paypal_config.client_id
        yield 'PAYPAL_CLIENT_SECRET', paypal_config.client_secret
        yield 'PAYPAL_ENVIRONMENT', paypal_config.environment

    stripe_config = config.payment_gateways.stripe
    if stripe_config and stripe_config.enabled:
        yield 'STRIPE_SECRET_KEY', stripe_config.secret_key
        yield 'STRIPE_PUBLISHABLE_KEY', stripe_config.publishable_key
        yield 'STRIPE_WEBHOOK_SECRET', stripe_config.webhook_secret

    # Skip property if not explicitly set (i.e. value is `None`). In
    # this case, Flask will propagate if debug mode or testing mode is
    # enabled.
    if config.propagate_exceptions is not None:
        yield 'PROPAGATE_EXCEPTIONS', config.propagate_exceptions

    yield 'REDIS_URL', config.redis.url

    yield 'SECRET_KEY', config.secret_key

    yield 'SQLALCHEMY_DATABASE_URI', assemble_database_uri(config.database)


def assemble_database_uri(db_config: DatabaseConfig) -> str:
    """Assemble SQLAlchemy database URL."""
    scheme = 'postgresql+psycopg'
    return f'{scheme}://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}'
