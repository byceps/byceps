"""
byceps.app_dispatcher
~~~~~~~~~~~~~~~~~~~~~

Serve multiple apps together.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from threading import Lock
from wsgiref.types import WSGIApplication

from flask import Flask
import structlog
from werkzeug.exceptions import InternalServerError, NotFound

from byceps.application import create_admin_app, create_api_app, create_site_app
from byceps.config.models import (
    AdminAppConfig,
    ApiAppConfig,
    BycepsConfig,
    SiteAppConfig,
    WebAppConfig,
)
from byceps.config.util import iterate_app_configs

from byceps.util.result import Err, Ok, Result

from .byceps_app import BycepsApp


log = structlog.get_logger()


def create_dispatcher_app(byceps_config: BycepsConfig) -> Flask:
    app = Flask('dispatcher')
    app.wsgi_app = AppDispatcher(byceps_config)
    return app


class AppDispatcher:
    def __init__(self, byceps_config: BycepsConfig) -> None:
        self.lock = Lock()
        self.app_configs_by_host: dict[str, WebAppConfig] = {
            app_config.server_name: app_config
            for app_config in iterate_app_configs(byceps_config.apps)
        }
        self.byceps_config = byceps_config
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

            match _create_app(app_config, self.byceps_config):
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
    app_config: WebAppConfig, byceps_config: BycepsConfig
) -> Result[BycepsApp, str]:
    match app_config:
        case AdminAppConfig():
            return Ok(create_admin_app(byceps_config, app_config))
        case ApiAppConfig():
            return Ok(create_api_app(byceps_config, app_config))
        case SiteAppConfig():
            site_id = app_config.site_id
            if not site_id:
                return Err(f'Unknown site ID "{site_id}"')

            app = create_site_app(byceps_config, app_config)
            return Ok(app)
        case _:
            return Err('Unknown or unsupported app configuration type')
