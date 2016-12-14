# -*- coding: utf-8 -*-

"""
Create and initialize the application using a configuration specified by
an environment variable.

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys

from byceps.application import create_app, init_app
from byceps.util.system import get_config_filename_from_env


try:
    config_filename = get_config_filename_from_env()
except Exception as e:
    sys.stderr.write("{}\n".format(e))
    sys.exit()

app = create_app(config_filename)
init_app(app)
