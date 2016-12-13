# -*- coding: utf-8 -*-

"""
application factory
~~~~~~~~~~~~~~~~~~~

Create and initialize the application using a configuration specified by
an environment variable.

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .application import create_app, init_app
from .util.system import get_config_filename_from_env


config_filename = get_config_filename_from_env()

app = create_app(config_filename)
init_app(app)
