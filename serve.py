"""
Create and initialize the application using a configuration specified by
an environment variable.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.application import create_app, init_app
from byceps.util.system import get_config_filename_from_env_or_exit


config_filename = get_config_filename_from_env_or_exit()

app = create_app(config_filename)
init_app(app)
