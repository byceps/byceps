# -*- coding: utf-8 -*-

"""
byceps.util.system
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os


CONFIG_ENV_VAR_NAME = 'BYCEPS_CONFIG'


def get_config_env_name_from_env():
    """Return the configuration environment name set via environment
    variable.

    Raise an exception if it isn't set.
    """
    env = os.environ.get(CONFIG_ENV_VAR_NAME)

    if not env:
        raise Exception(
            "No configuration environment was specified via the '{}' "
            "environment variable.".format(CONFIG_ENV_VAR_NAME))

    return env
