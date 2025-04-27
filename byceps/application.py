"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta
from typing import Any

from flask_babel import Babel
import jinja2
from redis import Redis
import structlog

from byceps.announce.announce import enable_announcements
from byceps.blueprints.admin import register_admin_blueprints
from byceps.blueprints.api import register_api_blueprints
from byceps.blueprints.site import register_site_blueprints
from byceps.config.converter import convert_config
from byceps.config.errors import ConfigurationError
from byceps.config.integration import (
    init_app as init_app_config,
    parse_value_from_environment,
)
from byceps.config.models import (
    AdminAppConfig,
    ApiAppConfig,
    AppConfig,
    AppMode,
    BycepsConfig,
    CliAppConfig,
    SiteAppConfig,
    WebAppConfig,
    WorkerAppConfig,
)
from byceps.database import db
from byceps.services.jobs.blueprints.admin.views import enable_rq_dashboard
from byceps.util import templatefilters
from byceps.util.authz import load_permissions
from byceps.util.l10n import get_current_user_locale
from byceps.util.templating import create_site_template_loader

from .byceps_app import BycepsApp


log = structlog.get_logger()


def create_admin_app(
    byceps_config: BycepsConfig, app_config: AdminAppConfig
) -> BycepsApp:
    app = _create_app(byceps_config, app_config)

    _log_app_state(app)

    return app


def create_site_app(
    byceps_config: BycepsConfig, app_config: SiteAppConfig
) -> BycepsApp:
    app = _create_app(byceps_config, app_config)

    _init_site_app(app)

    _log_app_state(app)

    return app


def create_api_app(
    byceps_config: BycepsConfig, app_config: ApiAppConfig
) -> BycepsApp:
    app = _create_app(byceps_config, app_config)

    register_api_blueprints(app)

    return app


def create_cli_app(byceps_config: BycepsConfig) -> BycepsApp:
    app_config = CliAppConfig()

    return _create_app(byceps_config, app_config)


def create_worker_app(byceps_config: BycepsConfig) -> BycepsApp:
    app_config = WorkerAppConfig()

    return _create_app(byceps_config, app_config)


def _create_app(
    byceps_config: BycepsConfig, app_config: AppConfig
) -> BycepsApp:
    """Create the actual Flask-based BYCEPS application."""
    app_mode = _get_app_mode(app_config)

    app = BycepsApp(app_mode, byceps_config)

    # Avoid connection errors after database becomes temporarily
    # unreachable, then becomes reachable again.
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

    _configure(app, byceps_config, app_config)

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

    load_permissions()

    app.byceps_feature_states['debug'] = app.debug

    metrics_enabled = (
        byceps_config.metrics.enabled and app.byceps_app_mode.is_admin()
    )
    app.byceps_feature_states['metrics'] = metrics_enabled

    style_guide_enabled = byceps_config.development.style_guide_enabled and (
        app_mode.is_admin() or app_mode.is_site()
    )
    app.byceps_feature_states['style_guide'] = style_guide_enabled

    if app_mode.is_admin():
        register_admin_blueprints(
            app,
            metrics_enabled=metrics_enabled,
            style_guide_enabled=style_guide_enabled,
        )
        _enable_rq_dashboard(app)
    elif app_mode.is_site():
        register_site_blueprints(app, style_guide_enabled=style_guide_enabled)

    templatefilters.register(app)

    _add_static_file_url_rules(app)

    enable_announcements()

    debug_toolbar_enabled = (
        byceps_config.development.toolbar_enabled
        and (app_mode.is_admin() or app_mode.is_site())
        and app.debug
    )
    if debug_toolbar_enabled:
        _enable_debug_toolbar(app)
    app.byceps_feature_states['debug_toolbar'] = debug_toolbar_enabled

    return app


def _get_app_mode(app_config: AppConfig) -> AppMode:
    """Derive application mode from application config."""
    match app_config:
        case AdminAppConfig():
            return AppMode.admin
        case ApiAppConfig():
            return AppMode.api
        case CliAppConfig():
            return AppMode.cli
        case SiteAppConfig():
            return AppMode.site
        case WorkerAppConfig():
            return AppMode.worker
        case _:
            raise ValueError('Unexpected application configuration type')


def _configure(
    app: BycepsApp, byceps_config: BycepsConfig, app_config: AppConfig
) -> None:
    """Configure application from file, environment variables, and defaults."""
    data = _assemble_configuration(byceps_config, app_config)
    app.config.from_mapping(data)

    init_app_config(app)


def _assemble_configuration(
    byceps_config: BycepsConfig, app_config: AppConfig
) -> dict[str, Any]:
    """Assemble configuration."""
    data = {
        # login sessions
        'PERMANENT_SESSION_LIFETIME': timedelta(14),
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'SESSION_COOKIE_SECURE': True,
        # Limit incoming request content.
        'MAX_CONTENT_LENGTH': 4000000,
    }

    data.update(convert_config(byceps_config))

    if isinstance(app_config, WebAppConfig):
        data['SERVER_NAME'] = app_config.server_name

    if isinstance(app_config, SiteAppConfig):
        data['SITE_ID'] = app_config.site_id

    # Allow configuration values to be overridden by environment variables.
    data.update(_get_config_from_environment())

    _ensure_required_config_keys(data)

    locale = data['LOCALE']
    data['BABEL_DEFAULT_LOCALE'] = locale

    timezone = data['TIMEZONE']
    data['BABEL_DEFAULT_TIMEZONE'] = timezone
    data['SHOP_ORDER_EXPORT_TIMEZONE'] = timezone

    return data


def _get_config_from_environment() -> dict[str, Any]:
    """Obtain selected config values from environment variables."""
    data = {}

    for key in (
        'REDIS_URL',
        'SECRET_KEY',
        'SESSION_COOKIE_SECURE',
        'SITE_ID',
        'SQLALCHEMY_DATABASE_URI',
    ):
        value = parse_value_from_environment(key)
        if value is not None:
            data[key] = value

    return data


def _ensure_required_config_keys(config: dict[str, Any]) -> None:
    """Ensure the required configuration keys have values."""
    for key in (
        'LOCALE',
        'REDIS_URL',
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI',
        'TIMEZONE',
    ):
        if not config.get(key):
            raise ConfigurationError(
                f'Missing value for configuration key "{key}".'
            )


def _add_static_file_url_rules(app: BycepsApp) -> None:
    """Add URL rules to for static files."""
    app.add_url_rule(
        '/static_sites/<site_id>/<path:filename>',
        endpoint='site_file',
        methods=['GET'],
        build_only=True,
    )


def _init_site_app(app: BycepsApp) -> None:
    """Initialize site application."""
    # Incorporate site-specific template overrides.
    app.jinja_loader = create_site_template_loader()


def _enable_debug_toolbar(app: BycepsApp) -> None:
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


def _enable_rq_dashboard(app: BycepsApp) -> None:
    app.config['RQ_DASHBOARD_REDIS_URL'] = app.config['REDIS_URL']
    enable_rq_dashboard(app, '/rq')
    app.byceps_feature_states['rq_dashboard'] = True


def _log_app_state(app: BycepsApp) -> None:
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
