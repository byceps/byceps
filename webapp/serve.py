# -*- coding: utf-8 -*-

import os
import sys

from byceps.application import create_app

environment = os.environ.get('ENVIRONMENT')

if environment is None:
    sys.stderr.write("Environment variable 'ENVIRONMENT' must be set but isn't.")
    sys.exit()

app = create_app(environment, initialize=True)
