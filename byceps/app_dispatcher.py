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
from typing import Annotated, Any, Literal
from wsgiref.types import WSGIApplication

from flask import Flask
from pydantic import BaseModel, Field, ValidationError
import rtoml
import structlog
from werkzeug.exceptions import InternalServerError, NotFound

from byceps.application import create_admin_app, create_api_app, create_site_app
from byceps.util.result import Err, Ok, Result


logger = structlog.get_logger()


class _BaseAppMount(BaseModel):
    server_name: str


class AdminAppMount(_BaseAppMount):
    mode: Literal['admin']


class ApiAppMount(_BaseAppMount):
    mode: Literal['api']


class SiteAppMount(_BaseAppMount):
    mode: Literal['site']
    site_id: str | None


AppMount = Annotated[
    AdminAppMount | ApiAppMount | SiteAppMount, Field(discriminator='mode')
]


class AppsConfig(BaseModel):
    app_mounts: list[AppMount] = Field(default_factory=list)


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
    try:
        data = rtoml.loads(toml)
    except rtoml.TomlParsingError as e:
        return Err(str(e))

    try:
        apps_config = AppsConfig.model_validate(data)
    except ValidationError as e:
        return Err(str(e))

    conflicting_server_names = _find_conflicting_server_names(apps_config)
    if conflicting_server_names:
        server_names_str = ', '.join(sorted(conflicting_server_names))
        return Err(f'Non-unique server names configured: {server_names_str}')

    return Ok(apps_config)


def _find_conflicting_server_names(apps_config: AppsConfig) -> set[str]:
    defined_server_names = set()
    conflicting_server_names = set()

    for mount in apps_config.app_mounts:
        server_name = mount.server_name
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
        self.mounts_by_host = {
            mount.server_name: mount for mount in apps_config.app_mounts
        }
        self.config_overrides = config_overrides
        self.apps_by_host: dict[str, WSGIApplication] = {}

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)

    def get_application(self, host_and_port) -> WSGIApplication:
        host = host_and_port.split(':')[0]

        with self.lock:
            app = self.apps_by_host.get(host)

            if app:
                return app

            log = logger.bind(host=host)

            mount = self.mounts_by_host.get(host)
            if not mount:
                log.debug('No application mounted for host')
                return NotFound()

            match _create_app(mount, config_overrides=self.config_overrides):
                case Ok(app):
                    self.apps_by_host[host] = app
                    mode = app.byceps_app_mode
                    if mode.is_site():
                        log = log.bind(site_id=app.config['SITE_ID'])
                    log.info('Application mounted', mode=mode.name)
                    return app
                case Err(e):
                    logger.error('Application creation failed', error=e)
                    return InternalServerError(e)
                case _:
                    error_message = 'Unknown error'
                    logger.error(
                        'Application creation failed', error=error_message
                    )
                    return InternalServerError(error_message)


def _create_app(
    mount: AppMount, *, config_overrides: dict[str, Any] | None = None
) -> Result[WSGIApplication, str]:
    match mount:
        case AdminAppMount():
            return Ok(create_admin_app(config_overrides=config_overrides))
        case ApiAppMount():
            return Ok(create_api_app(config_overrides=config_overrides))
        case SiteAppMount():
            site_id = mount.site_id
            if site_id:
                app = create_site_app(
                    site_id, config_overrides=config_overrides
                )
                return Ok(app)
            else:
                return Err(f'Unknown site ID "{site_id}"')
        case _:
            return Err(f'Unknown or unsupported app mode "{mount.mode}"')
