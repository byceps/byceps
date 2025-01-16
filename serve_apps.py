"""
Serve multiple apps together.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import sys

import structlog

from byceps.app_dispatcher import create_dispatcher_app, get_apps_config
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)
from byceps.util.result import Err, Ok
from byceps.util.sentry import configure_sentry_from_env


log = structlog.get_logger()


configure_sentry_from_env('apps')

config_overrides = read_configuration_from_file_given_in_env_var()

match get_apps_config():
    case Ok(apps_config):
        app = create_dispatcher_app(
            apps_config, config_overrides=config_overrides
        )
    case Err(e):
        log.error(e)
        sys.exit(1)
