"""
Serve multiple apps together.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import structlog

from byceps.app_dispatcher import create_dispatcher_app
from byceps.config.integration import (
    read_byceps_and_apps_configuration_from_file_given_in_env_var,
)
from byceps.util.sentry import configure_sentry_from_env


log = structlog.get_logger()


configure_sentry_from_env('apps')

byceps_config, apps_config = (
    read_byceps_and_apps_configuration_from_file_given_in_env_var()
)

app = create_dispatcher_app(byceps_config, apps_config)
