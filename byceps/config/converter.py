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

try:
    from .models import TurnstileConfig  
except Exception:  
    TurnstileConfig = None  

def convert_config(config: BycepsConfig) -> dict[str, Any]:
    """Convert configuration to dictionary accepted by Flask."""
    return dict(_generate_entries(config))


def _generate_entries(config: BycepsConfig) -> Iterator[tuple[str, Any]]:
    yield 'TESTING', config.testing

    yield 'LOCALE', config.locale

    timezone = config.timezone
    yield 'SHOP_ORDER_EXPORT_TIMEZONE', timezone
    yield 'TIMEZONE', timezone

    if config.propagate_exceptions is not None:
        yield 'PROPAGATE_EXCEPTIONS', config.propagate_exceptions

    yield 'REDIS_URL', config.redis.url

    yield 'SECRET_KEY', config.secret_key

    yield 'SQLALCHEMY_DATABASE_URI', assemble_database_uri(config.database)

    ts = getattr(config, 'turnstile', None)
    if ts is not None:
        enabled = bool(getattr(ts, 'enabled', False))
        sitekey = getattr(ts, 'sitekey', '') or ''
        secret  = getattr(ts, 'secret',  '') or ''

        yield 'TURNSTILE_ENABLED', enabled
        yield 'TURNSTILE_SITEKEY', sitekey
        yield 'TURNSTILE_SECRET',  secret

        yield 'turnstile', {
            'enabled': enabled,
            'sitekey': sitekey,
            'secret':  secret,
        }

def assemble_database_uri(db_config: DatabaseConfig) -> str:
    """Assemble SQLAlchemy database URL."""
    scheme = 'postgresql+psycopg'
    return f'{scheme}://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}'
