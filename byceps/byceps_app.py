"""
byceps.byceps_app
~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
from flask_babel import Babel
from redis import Redis

from byceps.config.models import (
    AdminWebAppConfig,
    ApiWebAppConfig,
    AppConfig,
    AppMode,
    BycepsConfig,
    CliAppConfig,
    SiteAppConfig,
    WorkerAppConfig,
)
from byceps.services.site.models import SiteID


class BycepsApp(Flask):
    def __init__(
        self,
        app_mode: AppMode,
        byceps_config: BycepsConfig,
        site_id: SiteID | None,
    ) -> None:
        super().__init__('byceps')

        self.babel_instance: Babel
        self.byceps_app_mode: AppMode = app_mode
        self.byceps_config: BycepsConfig = byceps_config
        self.byceps_feature_states: dict[str, bool] = {}
        self.redis_client: Redis
        self.site_id: SiteID | None = site_id


def create_byceps_app(
    byceps_config: BycepsConfig, app_config: AppConfig
) -> BycepsApp:
    app_mode = _get_app_mode(app_config)
    site_id = _get_site_id(app_config)

    return BycepsApp(app_mode, byceps_config, site_id)


def _get_app_mode(app_config: AppConfig) -> AppMode:
    """Derive application mode from application config."""
    match app_config:
        case AdminWebAppConfig():
            return AppMode.admin
        case ApiWebAppConfig():
            return AppMode.api
        case CliAppConfig():
            return AppMode.cli
        case SiteAppConfig():
            return AppMode.site
        case WorkerAppConfig():
            return AppMode.worker
        case _:
            raise ValueError('Unexpected application configuration type')


def _get_site_id(app_config: AppConfig) -> SiteID | None:
    """Return site ID for site application configurations, `None` otherwise."""
    match app_config:
        case SiteAppConfig():
            return app_config.site_id
        case _:
            return None
