"""
byceps.byceps_app
~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
from flask_babel import Babel
from redis import Redis

from byceps.config.models import AppMode


class BycepsApp(Flask):
    def __init__(self, app_mode: AppMode) -> None:
        super().__init__('byceps')

        self.babel_instance: Babel
        self.byceps_app_mode: AppMode = app_mode
        self.byceps_feature_states: dict[str, bool] = {}
        self.redis_client: Redis
