"""
byceps.app_dispatcher
~~~~~~~~~~~~~~~~~~~~~

Serve multiple apps together.

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os
from pathlib import Path
from threading import Lock
from typing import Any
from wsgiref.types import WSGIApplication

from flask import Flask
import structlog
from werkzeug.exceptions import InternalServerError, NotFound

from byceps.application import create_admin_app, create_api_app, create_site_app
from byceps.config.apps import parse_app_mounts_config
from byceps.config.models import (
    AdminAppConfig,
    ApiAppConfig,
    AppsConfig,
    SiteAppConfig,
)
from byceps.util.result import Err, Ok, Result


log = structlog.get_logger()


AppConfig = AdminAppConfig | ApiAppConfig | SiteAppConfig


def _get_all_app_configs(apps_config: AppsConfig) -> list[AppConfig]:
    all_app_configs: list[AppConfig] = []

    if apps_config.admin:
        all_app_configs.append(apps_config.admin)

    if apps_config.api:
        all_app_configs.append(apps_config.api)

    all_app_configs.extend(apps_config.sites)

    return all_app_configs


def get_apps_config() -> Result[AppsConfig, str]:
    return _get_apps_config_filename().and_then(_load_apps_config)


def _get_apps_config_filename() -> Result[Path, str]:
    filename_str = os.environ.get('BYCEPS_APPS_CONFIG')
    if not filename_str:
        return Err(
            'Please set environment variable BYCEPS_APPS_CONFIG to path of application mounts configuration file'
        )

    filename = Path(filename_str)
    return Ok(filename)


def _load_apps_config(path: Path) -> Result[AppsConfig, str]:
    if not path.exists():
        return Err(f'Applications configuration file "{path}" does not exist')

    toml = path.read_text()

    return parse_apps_config(toml).map_err(
        lambda e: f'Applications configuration file "{path}" contains errors:\n{e}'
    )


def parse_apps_config(toml: str) -> Result[AppsConfig, str]:
    def validate_server_names(apps_config: AppsConfig):
        conflicting_server_names = _find_conflicting_server_names(apps_config)
        if conflicting_server_names:
            server_names_str = ', '.join(sorted(conflicting_server_names))
            return Err(
                f'Non-unique server names configured: {server_names_str}'
            )
        else:
            return Ok(apps_config)

    return parse_app_mounts_config(toml).and_then(validate_server_names)


def _find_conflicting_server_names(apps_config: AppsConfig) -> set[str]:
    defined_server_names = set()
    conflicting_server_names = set()

    for app_config in _get_all_app_configs(apps_config):
        server_name = app_config.server_name
        if server_name in defined_server_names:
            conflicting_server_names.add(server_name)
        else:
            defined_server_names.add(server_name)

    return conflicting_server_names


def create_dispatcher_app(
    apps_config: AppsConfig,
    *,
    config_overrides: dict[str, Any] | None = None,
) -> WSGIApplication:
    app = Flask('dispatcher')
    app.wsgi_app = AppDispatcher(apps_config, config_overrides=config_overrides)
    return app


class AppDispatcher:
    def __init__(
        self,
        apps_config: AppsConfig,
        *,
        config_overrides: dict[str, Any] | None = None,
    ) -> None:
        self.lock = Lock()
        self.app_configs_by_host = {
            app_config.server_name: app_config
            for app_config in _get_all_app_configs(apps_config)
        }
        self.config_overrides = config_overrides
        self.apps_by_host: dict[str, WSGIApplication] = {}

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)

    def get_application(self, host_and_port) -> WSGIApplication:
        host = host_and_port.split(':')[0]

        log_ctx = log.bind(host=host)

        with self.lock:
            app = self.apps_by_host.get(host)

            if app:
                return app

            app_config = self.app_configs_by_host.get(host)
            if not app_config:
                log_ctx.debug('No application configured for host')
                return NotFound()

            match _create_app(
                app_config, config_overrides=self.config_overrides
            ):
                case Ok(app):
                    self.apps_by_host[host] = app
                    mode = app.byceps_app_mode
                    if mode.is_site():
                        log_ctx = log_ctx.bind(site_id=app.config['SITE_ID'])
                    log_ctx.info('Application mounted', mode=mode.name)
                    return app
                case Err(e):
                    log_ctx.error('Application creation failed', error=e)
                    return InternalServerError(e)
                case _:
                    error_message = 'Unknown error'
                    log_ctx.error(
                        'Application creation failed', error=error_message
                    )
                    return InternalServerError(error_message)


def _create_app(
    app_config: AppConfig, *, config_overrides: dict[str, Any] | None = None
) -> Result[Flask, str]:
    match app_config:
        case AdminAppConfig():
            return Ok(create_admin_app(config_overrides=config_overrides))
        case ApiAppConfig():
            return Ok(create_api_app(config_overrides=config_overrides))
        case SiteAppConfig():
            site_id = app_config.site_id
            if site_id:
                app = create_site_app(
                    site_id, config_overrides=config_overrides
                )
                return Ok(app)
            else:
                return Err(f'Unknown site ID "{site_id}"')
        case _:
            return Err('Unknown or unsupported app configuration type')
