# -*- coding: utf-8 -*-

"""
byceps.util.system
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import os


def get_config_env_name_from_env():
    """Return the configuration environment name set via environment variable.

    Raise an exception if it isn't set.
    """
    env = os.environ.get('ENV')

    if env is None:
        raise Exception(
            "No configuration environment was specified via the 'ENV' "
            "environment variable.")

    return env
