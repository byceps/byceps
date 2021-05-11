"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from http import HTTPStatus
from importlib import import_module
import os
from pathlib import Path
from typing import Any, Callable, Optional, Union

from flask import current_app, Flask, g, redirect
from flask_babel import Babel
import jinja2
from redis import StrictRedis

from .blueprints.blueprints import register_blueprints
from . import config, config_defaults
from .database import db
from . import email
from .util.l10n import set_locale
from .util import templatefilters
from .util.templating import SiteTemplateOverridesLoader
from .util.views import redirect_to


def create_app(
    *,
    config_filename: Optional[Union[Path, str]] = None,
    config_overrides: Optional[dict[str, Any]] = None,
) -> Flask:
    """Create the actual Flask application."""
    app = Flask('byceps')

    app.config.from_object(config_defaults)
    if config_filename is not None:
        app.config.from_pyfile(str(config_filename))
    else:
        app.config.from_envvar('BYCEPS_CONFIG')
    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    # Allow database URI to be overriden via environment variable.
    sqlalchemy_database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if sqlalchemy_database_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_uri

    config.init_app(app)

    # Throw an exception when an undefined name is referenced in a template.
    # NB: Set via `app.jinja_options['undefined'] = ` instead of
    #     `app.jinja_env.undefined = ` as that would create the Jinja
    #      environment too early.
    app.jinja_options['undefined'] = jinja2.StrictUndefined

    # Set the locale.
    set_locale(app.config['LOCALE'])  # Fail if not configured.

    babel = Babel(app)
    babel.locale_selector_func = _get_user_locale

    # Initialize database.
    db.init_app(app)

    # Initialize Redis client.
    app.redis_client = StrictRedis.from_url(app.config['REDIS_URL'])

    email.init_app(app)

    register_blueprints(app)

    templatefilters.register(app)

    _add_static_file_url_rules(app)

    app_mode = config.get_app_mode(app)
    if app_mode.is_admin():
        _init_admin_app(app)
    elif app_mode.is_site():
        _init_site_app(app)

    _load_announce_signal_handlers()

    return app


def _get_user_locale() -> Optional[str]:
    return g.user.locale


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
    app.add_url_rule(
        '/',
        endpoint='root',
        view_func=lambda: redirect_to('admin_dashboard.view_global'),
    )

    if app.config['RQ_DASHBOARD_ENABLED']:
        import rq_dashboard

        app.register_blueprint(rq_dashboard.blueprint, url_prefix='/admin/rq')


def _init_site_app(app: Flask) -> None:
    """Initialize site application."""
    _set_url_root_path(app)

    # Incorporate site-specific template overrides.
    app.jinja_loader = SiteTemplateOverridesLoader()

    # Set up site-aware template context processor.
    app._site_context_processors = {}
    app.context_processor(_get_site_template_context)


def _set_url_root_path(app: Flask) -> None:
    """Set an optional URL path to redirect to from the root URL path (`/`).

    Important: Don't specify the target with a leading slash unless you
    really mean the root of the host.
    """
    target_url = app.config['ROOT_REDIRECT_TARGET']
    if target_url is None:
        return

    def _redirect():
        return redirect(target_url, code=HTTPStatus.TEMPORARY_REDIRECT)

    app.add_url_rule('/', endpoint='root', view_func=_redirect)


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
) -> Optional[Callable[[], dict[str, Any]]]:
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
) -> Optional[Callable[[], dict[str, Any]]]:
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


def _load_announce_signal_handlers() -> None:
    """Import modules containing handlers so they connect to the
    corresponding signals.
    """
    from .announce import connections
