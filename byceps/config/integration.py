"""
byceps.config.integration
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import json
import os
from pathlib import Path

import structlog

from byceps.util.result import Err, Ok

from .errors import ConfigurationError
from .models import AppsConfig, BycepsConfig
from .parser import parse_config


log = structlog.get_logger()


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


def read_configuration_from_file_given_in_env_var() -> BycepsConfig:
    """Load configuration from file specified via environment variable."""
    byceps_config, _ = (
        read_byceps_and_apps_configuration_from_file_given_in_env_var()
    )
    return byceps_config


def read_byceps_and_apps_configuration_from_file_given_in_env_var() -> tuple[
    BycepsConfig, AppsConfig
]:
    """Load configuration from file specified via environment variable."""
    filename_str = os.environ.get('BYCEPS_CONFIG_FILE')

    if not filename_str:
        error_message = 'No configuration file specified. Use environment variable `BYCEPS_CONFIG_FILE`.'
        log.error(error_message)
        raise ConfigurationError(error_message)

    filename = Path(filename_str)
    byceps_config = _read_configuration_from_file(filename)
    return byceps_config, byceps_config.apps


def _read_configuration_from_file(filename: Path) -> BycepsConfig:
    """Load configuration from file."""
    match parse_config(filename.read_text()):
        case Ok(config):
            return config
        case Err(errors):
            log.error(
                'Could not parse configuration file.',
                filename=filename,
                errors=errors,
            )
            raise ConfigurationError('Errors found in configuration file.')
