# -*- coding: utf-8 -*-

"""
byceps.util.framework.config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration utilities

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path


def load_config(app, environment_name):
    """Load the configuration for the specified environment from the
    corresponding module.

    The module is expected to be located in the 'config/env'
    sub-package.
    """
    filename = _assemble_config_filename(app, environment_name)

    app.config.from_pyfile(filename)


def _assemble_config_filename(app, environment_name):
    root = Path(app.root_path)
    filename = '{}.py'.format(environment_name)

    return str(root / '..' / 'config' / 'env' / filename)
