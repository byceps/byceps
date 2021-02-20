"""
byceps.util.system
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os

from ..config import ConfigurationError


def get_env_value(name: str, error_message: str) -> str:
    """Return the value of the environment variable.

    Raise an exception if it isn't set or if it is empty.
    """
    env = os.environ.get(name)

    if not env:
        raise ConfigurationError(error_message)

    return env
