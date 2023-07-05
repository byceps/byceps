"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterator
from importlib import import_module
import os
from pathlib import Path
from typing import Any, Callable

from flask import abort, current_app, Flask, g
from flask_babel import Babel
import jinja2
from redis import Redis
import rtoml
import structlog

from byceps import config, config_defaults
from byceps.announce.announce import enable_announcements
from byceps.blueprints.blueprints import register_blueprints
from byceps.config import ConfigurationError
from byceps.database import db
from byceps.util import templatefilters, templatefunctions
from byceps.util.authorization import (
    has_current_user_permission,
    load_permissions,
)
from byceps.util.l10n import get_current_user_locale
from byceps.util.templating import SiteTemplateOverridesLoader


log = structlog.get_logger()


def get_app_factory():
    """Return a function to create the application based on the
    environment.
    """
    app_mode = os.environ.get('APP_MODE')

    if app_mode == 'admin':
        return create_admin_app
    elif app_mode == 'site':
        return create_site_app
    else:
        raise ConfigurationError(
            'Unknown or no app mode configured for configuration key "APP_MODE".'
        )


def create_admin_app(
    *,
    config_filename: Path | str | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['APP_MODE'] = 'admin'

    return create_app(
        config_filename=config_filename,
        config_overrides=config_overrides,
    )


def create_site_app(
    *,
    config_filename: Path | str | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['APP_MODE'] = 'site'

    return create_app(
        config_filename=config_filename,
        config_overrides=config_overrides,
    )


def create_app(
    *,
    config_filename: Path | str | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> Flask:
    """Create the actual Flask application."""
    app = Flask('byceps')

    _configure(app, config_filename, config_overrides)

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

    app_mode = config.get_app_mode(app)

    load_permissions()

    register_blueprints(app, app_mode)

    templatefilters.register(app)
    templatefunctions.register(app)

    _add_static_file_url_rules(app)

    if app_mode.is_admin():
        _init_admin_app(app)
    elif app_mode.is_site():
        _init_site_app(app)

    enable_announcements()

    if app.debug and app.config.get('DEBUG_TOOLBAR_ENABLED', False):
        _enable_debug_toolbar(app)

    log.info('Application created', app_mode=app_mode.name, debug=app.debug)

    return app


def _configure(
    app: Flask,
    config_filename: Path | str | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> None:
    """Configure application from file, environment variables, and defaults."""
    app.config.from_object(config_defaults)

    if config_filename is None:
        config_filename = os.environ.get('BYCEPS_CONFIG')

    if config_filename is not None:
        if isinstance(config_filename, str):
            config_filename = Path(config_filename)

        if config_filename.suffix == '.py':
            app.config.from_pyfile(str(config_filename))
        else:
            app.config.from_file(str(config_filename), load=rtoml.load)

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    # Allow configuration values to be overridden by environment variables.
    app.config.update(_get_config_from_environment())

    _ensure_required_config_keys(app)

    config.init_app(app)


def _get_config_from_environment() -> Iterator[tuple[str, str]]:
    """Obtain selected config values from environment variables."""
    for key in (
        'APP_MODE',
        'MAIL_HOST',
        'MAIL_PASSWORD',
        'MAIL_PORT',
        'MAIL_STARTTLS',
        'MAIL_SUPPRESS_SEND',
        'MAIL_USE_SSL',
        'MAIL_USERNAME',
        'METRICS_ENABLED',
        'REDIS_URL',
        'SECRET_KEY',
        'SITE_ID',
        'SQLALCHEMY_DATABASE_URI',
    ):
        value = os.environ.get(key)
        if value:
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
        '/sites/<site_id>/<path:filename>',
        endpoint='site_file',
        methods=['GET'],
        build_only=True,
    )


def _init_admin_app(app: Flask) -> None:
    """Initialize admin application."""
    _enable_rq_dashboard(app)


def _init_site_app(app: Flask) -> None:
    """Initialize site application."""
    # Incorporate site-specific template overrides.
    app.jinja_loader = SiteTemplateOverridesLoader()

    # Set up site-aware template context processor.
    app._site_context_processors = {}
    app.context_processor(_get_site_template_context)


def _get_site_template_context() -> dict[str, Any]:
    """Return the site-specific additions to the template context."""
    site_context_processor = _find_site_template_context_processor_cached(
        g.site_id
    )

    if not site_context_processor:
        return {}

    return site_context_processor()


def _find_site_template_context_processor_cached(
    site_id: str,
) -> Callable[[], dict[str, Any]] | None:
    """Return the template context processor for the site.

    A processor will be cached after it has been obtained for the first
    time.
    """
    # `None` is a valid value for a site that does not specify a
    # template context processor.

    if site_id in current_app._site_context_processors:
        return current_app._site_context_processors.get(site_id)
    else:
        context_processor = _find_site_template_context_processor(site_id)
        current_app._site_context_processors[site_id] = context_processor
        return context_processor


def _find_site_template_context_processor(
    site_id: str,
) -> Callable[[], dict[str, Any]] | None:
    """Import a template context processor from the site's package.

    If a site package contains a module named `extension` and that
    contains a top-level callable named `template_context_processor`,
    then that callable is imported and returned.
    """
    module_name = f'sites.{site_id}.extension'
    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        # No extension module found in site package.
        return None

    context_processor = getattr(module, 'template_context_processor', None)
    if context_processor is None:
        # Context processor not found in module.
        return None

    if not callable(context_processor):
        # Context processor object is not callable.
        return None

    return context_processor


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
    log.info('Debug toolbar enabled')


def _enable_rq_dashboard(app: Flask) -> None:
    import rq_dashboard

    @rq_dashboard.blueprint.before_request
    def require_permission():
        if not has_current_user_permission('jobs.view'):
            abort(403)

    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/admin/rq')

    log.info('RQ dashboard enabled')
