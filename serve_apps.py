"""
Serve multiple apps together.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import structlog

from byceps.app_dispatcher import create_dispatcher_app
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)
from byceps.util.sentry import configure_sentry_from_env


log = structlog.get_logger()


configure_sentry_from_env('apps')

config = read_configuration_from_file_given_in_env_var()

app = create_dispatcher_app(config)
