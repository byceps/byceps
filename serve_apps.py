"""
Serve multiple apps together.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import structlog

from byceps.app_dispatcher import create_dispatcher_app
from byceps.config.converter import convert_config
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)
from byceps.util.sentry import configure_sentry_from_env


log = structlog.get_logger()


configure_sentry_from_env('apps')

config = read_configuration_from_file_given_in_env_var()
config_overrides = convert_config(config)

app = create_dispatcher_app(config.apps, config_overrides=config_overrides)
