"""
byceps.util.system
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os
import sys


CONFIG_VAR_NAME = 'BYCEPS_CONFIG'


def get_config_filename_from_env() -> str:
    """Return the configuration filename set via environment variable.

    Raise an exception if it isn't set.
    """
    env = os.environ.get(CONFIG_VAR_NAME)

    if not env:
        raise Exception(
            "No configuration file was specified via the '{}' "
            "environment variable.".format(CONFIG_VAR_NAME))

    return env


def get_config_filename_from_env_or_exit() -> str:
    """Return the configuration filename set via environment variable.

    Exit if it isn't set.
    """
    try:
        return get_config_filename_from_env()
    except Exception as e:
        sys.stderr.write("{}\n".format(e))
        sys.exit(1)
