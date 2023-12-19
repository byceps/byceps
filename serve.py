"""
Create and initialize the admin or site application, based on the
environment.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os

from byceps.application import create_admin_app, create_api_app, create_site_app
from byceps.config import ConfigurationError
from byceps.util.sentry import configure_sentry_from_env


configure_sentry_from_env()

match os.environ.get('APP_MODE'):
    case 'admin':
        app = create_admin_app()
    case 'api':
        app = create_api_app()
    case 'site':
        site_id = os.environ.get('SITE_ID')
        if not site_id:
            raise ConfigurationError(
                'No site ID specified via environment variable "SITE_ID".'
            )

        app = create_site_app(site_id)
    case _:
        raise ConfigurationError(
            'Unknown or no app mode specified via environment variable "APP_MODE".'
        )
