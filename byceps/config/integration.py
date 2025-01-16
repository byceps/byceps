"""
byceps.config.integration
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import json
import os
from pathlib import Path
from typing import Any

import rtoml

from byceps.byceps_app import BycepsApp

from .errors import ConfigurationError


def init_app(app: BycepsApp) -> None:
    if app.byceps_app_mode.is_site():
        if not app.config.get('SITE_ID'):
            raise ConfigurationError('No site ID configured.')


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


def read_configuration_from_file_given_in_env_var() -> dict[str, Any]:
    """Load configuration from file specified via environment variable."""
    filename_str = os.environ.get('BYCEPS_CONFIG')
    if not filename_str:
        return {}

    filename = Path(filename_str)
    return _read_configuration_from_file(filename)


def _read_configuration_from_file(filename: Path) -> dict[str, Any]:
    """Load configuration from file."""
    try:
        with filename.open() as f:
            return rtoml.load(f)
    except OSError as e:
        e.strerror = f'Unable to load configuration file ({e.strerror})'
        raise
