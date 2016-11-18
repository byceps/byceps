# -*- coding: utf-8 -*-

import os
import sys

from byceps.application import create_app, init_app


CONFIG_ENV_VAR_NAME = 'ENVIRONMENT'


environment = os.environ.get(CONFIG_ENV_VAR_NAME)

if environment is None:
    sys.stderr.write("Environment variable '{}' must be set but isn't."
                     .format(CONFIG_ENV_VAR_NAME))
    sys.exit()

app = create_app(environment)
init_app(app)
