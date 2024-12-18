"""
byceps.config.integration
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import json
import os

from flask import Flask

from .errors import ConfigurationError
from .models import AppMode


def init_app(app: Flask) -> None:
    app.byceps_app_mode = _determine_app_mode(app)

    if app.byceps_app_mode.is_site():
        if not app.config.get('SITE_ID'):
            raise ConfigurationError('No site ID configured.')


def _determine_app_mode(app: Flask) -> AppMode:
    value = app.config.get('APP_MODE', 'base')

    try:
        return AppMode[value]
    except KeyError as exc:
        raise ConfigurationError(
            f'Invalid app mode "{value}" configured.'
        ) from exc


def parse_value_from_environment(
    key: str,
) -> bool | dict | float | int | list | str | None:
    value = os.environ.get(key)
    if value is None:
        return None

    try:
        # Detect booleans, numbers, collections, `null`/`None`.
        return json.loads(value)
    except Exception:
        # Leave it as a string.
        return value
