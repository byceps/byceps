"""
Create and initialize the site application.

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os

from byceps.application import create_site_app
from byceps.config.errors import ConfigurationError
from byceps.util.sentry import configure_sentry_from_env


configure_sentry_from_env()


site_id = os.environ.get('SITE_ID')
if not site_id:
    raise ConfigurationError(
        'No site ID specified via environment variable "SITE_ID".'
    )

app = create_site_app(site_id)
