"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
import os
from pathlib import Path
from typing import Any

from flask import Flask
from flask_babel import Babel
import jinja2
from redis import Redis
import rtoml
import structlog
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from byceps import config, config_defaults
from byceps.announce.announce import enable_announcements
from byceps.blueprints.admin.blueprints import register_admin_blueprints
from byceps.blueprints.admin.jobs.views import enable_rq_dashboard
from byceps.blueprints.api.blueprints import register_api_blueprints
from byceps.blueprints.site.blueprints import register_site_blueprints
from byceps.config import (
    AppMode,
    ConfigurationError,
    parse_value_from_environment,
)
from byceps.database import db
from byceps.paypal import paypal
from byceps.util import templatefilters
from byceps.util.authz import load_permissions
from byceps.util.framework.blueprint import get_blueprint
from byceps.util.l10n import get_current_user_locale
from byceps.util.templating import SiteTemplateOverridesLoader


log = structlog.get_logger()


def create_admin_app(
    *, config_overrides: dict[str, Any] | None = None
) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['APP_MODE'] = 'admin'

    app = _create_app(config_overrides=config_overrides)

    _dispatch_apps_by_url_path(app, config_overrides)

    _log_app_state(app)

    return app


def create_site_app(
    site_id: str, *, config_overrides: dict[str, Any] | None = None
) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['SITE_ID'] = site_id
    config_overrides['APP_MODE'] = 'site'

    app = _create_app(config_overrides=config_overrides)

    _init_site_app(app)

    _log_app_state(app)

    return app


def create_api_app(*, config_overrides: dict[str, Any] | None = None) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['APP_MODE'] = 'api'

    app = _create_app(config_overrides=config_overrides)

    register_api_blueprints(app)

    return app


def create_cli_app() -> Flask:
    config_overrides = {
        'APP_MODE': 'cli',
        'DEBUG_TOOLBAR_ENABLED': False,
        'METRICS_ENABLED': False,
        'STYLE_GUIDE_ENABLED': False,
    }

    return _create_app(config_overrides=config_overrides)


def create_metrics_app(database_uri: str) -> Flask:
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    db.init_app(app)

    blueprint = get_blueprint('monitoring.metrics')
    app.register_blueprint(blueprint)

    return app


def create_worker_app() -> Flask:
    config_overrides = {
        'APP_MODE': 'worker',
        'DEBUG_TOOLBAR_ENABLED': False,
        'METRICS_ENABLED': False,
        'STYLE_GUIDE_ENABLED': False,
    }

    return _create_app(config_overrides=config_overrides)


def _create_app(*, config_overrides: dict[str, Any] | None = None) -> Flask:
    """Create the actual Flask application."""
    app = Flask('byceps')

    _configure(app, config_overrides)

    app_mode = app.byceps_app_mode

    # Throw an exception when an undefined name is referenced in a template.
    # NB: Set via `app.jinja_options['undefined'] = ` instead of
    #     `app.jinja_env.undefined = ` as that would create the Jinja
    #      environment too early.
    app.jinja_options['undefined'] = jinja2.StrictUndefined

    app.babel_instance = Babel(app, locale_selector=get_current_user_locale)

    # Initialize database.
    db.init_app(app)

    # Initialize Redis client.
    app.redis_client = Redis.from_url(app.config['REDIS_URL'])

    paypal.init_app(app)

    load_permissions()

    app.byceps_feature_states: dict[str, bool] = {
        'debug': app.debug,
    }

    style_guide_enabled = app.config.get('STYLE_GUIDE_ENABLED', False) and (
        app_mode.is_admin() or app_mode.is_site()
    )
    app.byceps_feature_states['style_guide'] = style_guide_enabled

    if app_mode.is_admin():
        register_admin_blueprints(app, style_guide_enabled=style_guide_enabled)
        _enable_rq_dashboard(app)
    elif app_mode.is_site():
        register_site_blueprints(app, style_guide_enabled=style_guide_enabled)

    templatefilters.register(app)

    _add_static_file_url_rules(app)

    enable_announcements()

    debug_toolbar_enabled = (
        app.config.get('DEBUG_TOOLBAR_ENABLED', False)
        and (app_mode.is_admin() or app_mode.is_site())
        and app.debug
    )
    if debug_toolbar_enabled:
        _enable_debug_toolbar(app)
    app.byceps_feature_states['debug_toolbar'] = debug_toolbar_enabled

    return app


def _configure(
    app: Flask, config_overrides: dict[str, Any] | None = None
) -> None:
    """Configure application from file, environment variables, and defaults."""
    app.config.from_object(config_defaults)

    config_filename_str = os.environ.get('BYCEPS_CONFIG')
    if config_filename_str:
        config_filename = Path(config_filename_str)
        app.config.from_file(str(config_filename), load=rtoml.load)

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    # Allow configuration values to be overridden by environment variables.
    app.config.update(_get_config_from_environment())

    _ensure_required_config_keys(app)

    config.init_app(app)


def _get_config_from_environment() -> Iterator[tuple[str, Any]]:
    """Obtain selected config values from environment variables."""
    for key in (
        'APP_MODE',
        'DEBUG',
        'DEBUG_TOOLBAR_ENABLED',
        'MAIL_HOST',
        'MAIL_PASSWORD',
        'MAIL_PORT',
        'MAIL_STARTTLS',
        'MAIL_SUPPRESS_SEND',
        'MAIL_USE_SSL',
        'MAIL_USERNAME',
        'METRICS_ENABLED',
        'PROPAGATE_EXCEPTIONS',
        'REDIS_URL',
        'SECRET_KEY',
        'SESSION_COOKIE_SECURE',
        'SITE_ID',
        'SQLALCHEMY_DATABASE_URI',
        'STYLE_GUIDE_ENABLED',
    ):
        value = parse_value_from_environment(key)
        if value is not None:
            yield key, value


def _ensure_required_config_keys(app: Flask) -> None:
    """Ensure the required configuration keys have values."""
    for key in (
        'APP_MODE',
        'REDIS_URL',
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI',
    ):
        if not app.config.get(key):
            raise ConfigurationError(
                f'Missing value for configuration key "{key}".'
            )


def _add_static_file_url_rules(app: Flask) -> None:
    """Add URL rules to for static files."""
    app.add_url_rule(
        '/static_sites/<site_id>/<path:filename>',
        endpoint='site_file',
        methods=['GET'],
        build_only=True,
    )


def _init_site_app(app: Flask) -> None:
    """Initialize site application."""
    # Incorporate site-specific template overrides.
    app.jinja_loader = SiteTemplateOverridesLoader()


def _dispatch_apps_by_url_path(
    app: Flask,
    config_overrides: dict[str, Any] | None,
) -> None:
    mounts = {}

    metrics_enabled = (
        app.config['METRICS_ENABLED'] and app.byceps_app_mode.is_admin()
    )
    if metrics_enabled:
        metrics_app = create_metrics_app(app.config['SQLALCHEMY_DATABASE_URI'])
        mounts['/metrics'] = metrics_app
    app.byceps_feature_states['metrics'] = metrics_enabled

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, mounts)


def _enable_debug_toolbar(app: Flask) -> None:
    try:
        from flask_debugtoolbar import DebugToolbarExtension
    except ImportError:
        log.warning(
            'Could not import Flask-DebugToolbar. '
            '`pip install Flask-DebugToolbar` should make it available.'
        )
        return

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)


def _enable_rq_dashboard(app: Flask) -> None:
    app.config['RQ_DASHBOARD_REDIS_URL'] = app.config['REDIS_URL']
    enable_rq_dashboard(app, '/rq')
    app.byceps_feature_states['rq_dashboard'] = True


def _log_app_state(app: Flask) -> None:
    event_kw = {'app_mode': app.byceps_app_mode.name}

    features = {
        name: (enabled and 'enabled' or 'disabled')
        for name, enabled in app.byceps_feature_states.items()
    }
    event_kw.update(features)

    match app.byceps_app_mode:
        case AppMode.site:
            event_kw['site_id'] = app.config['SITE_ID']

    log.info('Application created', **event_kw)
