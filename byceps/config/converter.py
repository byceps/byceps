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
    # TurnstileConfig ist in deinem Fork neu – Import optional absichern,
    # damit ältere Umgebungen nicht crashen.
    from .models import TurnstileConfig  # type: ignore
except Exception:  # pragma: no cover
    TurnstileConfig = None  # type: ignore[misc]

def convert_config(config: BycepsConfig) -> dict[str, Any]:
    """Convert configuration to dictionary accepted by Flask."""
    return dict(_generate_entries(config))


def _generate_entries(config: BycepsConfig) -> Iterator[tuple[str, Any]]:
    yield 'TESTING', config.testing

    yield 'LOCALE', config.locale

    timezone = config.timezone
    yield 'SHOP_ORDER_EXPORT_TIMEZONE', timezone
    yield 'TIMEZONE', timezone

    # Skip property if not explicitly set (i.e. value is `None`). In
    # this case, Flask will propagate if debug mode or testing mode is
    # enabled.
    if config.propagate_exceptions is not None:
        yield 'PROPAGATE_EXCEPTIONS', config.propagate_exceptions

    yield 'REDIS_URL', config.redis.url

    yield 'SECRET_KEY', config.secret_key

    yield 'SQLALCHEMY_DATABASE_URI', assemble_database_uri(config.database)

    # --- Cloudflare Turnstile in app.config spiegeln ---
    # parser.py liefert dir config.turnstile (optional, mit Defaults).
    ts = getattr(config, 'turnstile', None)
    if ts is not None:
        enabled = bool(getattr(ts, 'enabled', False))
        sitekey = getattr(ts, 'sitekey', '') or ''
        secret  = getattr(ts, 'secret',  '') or ''

        # Uppercase Keys: für Zugriff via config.get('TURNSTILE_ENABLED') in Jinja/Views
        yield 'TURNSTILE_ENABLED', enabled
        yield 'TURNSTILE_SITEKEY', sitekey
        yield 'TURNSTILE_SECRET',  secret

        # Optional als Dict (falls du es in Templates hübsch brauchst: {{ turnstile.enabled }})
        yield 'turnstile', {
            'enabled': enabled,
            'sitekey': sitekey,
            'secret':  secret,
        }

def assemble_database_uri(db_config: DatabaseConfig) -> str:
    """Assemble SQLAlchemy database URL."""
    scheme = 'postgresql+psycopg'
    return f'{scheme}://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}'
