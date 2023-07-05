"""
Create and initialize the application using a configuration specified by
an environment variable.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


from byceps.application import get_app_factory
from byceps.util.sentry import configure_sentry_from_env


configure_sentry_from_env()

app_factory = get_app_factory()
app = app_factory()
