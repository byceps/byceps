"""
byceps.byceps_app
~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
from flask_babel import Babel
from redis import Redis

from byceps.config.models import AppMode, BycepsConfig


class BycepsApp(Flask):
    def __init__(
        self,
        app_mode: AppMode,
        byceps_config: BycepsConfig,
        site_id: str | None,
    ) -> None:
        super().__init__('byceps')

        self.babel_instance: Babel
        self.byceps_app_mode: AppMode = app_mode
        self.byceps_config: BycepsConfig = byceps_config
        self.byceps_feature_states: dict[str, bool] = {}
        self.redis_client: Redis
        self.site_id = site_id
