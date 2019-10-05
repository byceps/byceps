"""
byceps.util.system
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os
import sys

from ..config import ConfigurationError


CONFIG_VAR_NAME = 'BYCEPS_CONFIG'


def get_config_filename_from_env() -> str:
    """Return the configuration filename set via environment variable.

    Raise an exception if it isn't set.
    """
    error_message = "No configuration file was specified via the " \
                    f"'{CONFIG_VAR_NAME}' environment variable."

    return get_env_value(CONFIG_VAR_NAME, error_message)


def get_env_value(name: str, error_message: str) -> str:
    """Return the value of the environment variable.

    Raise an exception if it isn't set or if it is empty.
    """
    env = os.environ.get(name)

    if not env:
        raise ConfigurationError(error_message)

    return env


def get_config_filename_from_env_or_exit() -> str:
    """Return the configuration filename set via environment variable.

    Exit if it isn't set.
    """
    try:
        return get_config_filename_from_env()
    except ConfigurationError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)
