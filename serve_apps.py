"""
Serve multiple web apps together.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import structlog

from byceps.config.integration import (
    read_byceps_and_apps_configuration_from_file_given_in_env_var,
)
from byceps.util.sentry import configure_sentry_from_env
from byceps.web_apps_dispatcher import create_web_apps_dispatcher_app


log = structlog.get_logger()


configure_sentry_from_env('apps')

byceps_config, web_apps_config = (
    read_byceps_and_apps_configuration_from_file_given_in_env_var()
)

app = create_web_apps_dispatcher_app(byceps_config, web_apps_config)
