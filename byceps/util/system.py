# -*- coding: utf-8 -*-

"""
byceps.util.system
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os


CONFIG_VAR_NAME = 'BYCEPS_CONFIG'


def get_config_filename_from_env():
    """Return the configuration filename set via environment variable.

    Raise an exception if it isn't set.
    """
    env = os.environ.get(CONFIG_VAR_NAME)

    if not env:
        raise Exception(
            "No configuration file was specified via the '{}' "
            "environment variable.".format(CONFIG_VAR_NAME))

    return env
