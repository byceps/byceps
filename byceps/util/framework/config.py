# -*- coding: utf-8 -*-

"""
byceps.util.framework.config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration utilities

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path


def assemble_config_filename(environment_name):
    """Assemble a full config filename from an environment name."""
    root = Path('..')
    filename = '{}.py'.format(environment_name)

    return root / 'config' / 'env' / filename
