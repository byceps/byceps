"""
Create and initialize the admin or site application, based on the
environment.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os

from byceps.application import create_admin_app, create_site_app
from byceps.config import ConfigurationError
from byceps.util.sentry import configure_sentry_from_env


configure_sentry_from_env()

app_mode = os.environ.get('APP_MODE')
if app_mode == 'admin':
    app = create_admin_app()
elif app_mode == 'site':
    app = create_site_app()
else:
    raise ConfigurationError(
        'Unknown or no app mode configured for configuration key "APP_MODE".'
    )
