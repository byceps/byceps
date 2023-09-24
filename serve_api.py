"""
Create and initialize the API application.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.application import create_api_app
from byceps.util.sentry import configure_sentry_from_env


configure_sentry_from_env()

app = create_api_app()
