"""
Serve multiple apps together.

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import sys

import structlog

from byceps.app_dispatcher import create_dispatcher_app, get_apps_config
from byceps.util.result import Err, Ok


log = structlog.get_logger()


match get_apps_config():
    case Ok(apps_config):
        app = create_dispatcher_app(apps_config)
    case Err(e):
        log.error(e)
        sys.exit(1)
