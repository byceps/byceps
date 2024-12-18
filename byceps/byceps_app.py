"""
byceps.byceps_app
~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
from flask_babel import Babel
from redis import Redis

from byceps.config.models import AppMode


class BycepsApp(Flask):
    def __init__(self) -> None:
        super().__init__('byceps')

        self.babel_instance: Babel
        self.byceps_app_mode: AppMode
        self.byceps_feature_states: dict[str, bool] = {}
        self.redis_client: Redis
