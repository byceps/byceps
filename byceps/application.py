"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from importlib import import_module
import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional, Tuple, Union

from flask import current_app, Flask, g, redirect
import jinja2

from . import config, config_defaults
from .database import db
from . import email
from .redis import redis
from .util.framework.blueprint import register_blueprint
from .util.l10n import set_locale
from .util import templatefilters
from .util.templating import SiteTemplateOverridesLoader


BlueprintReg = Tuple[str, Optional[str]]


def create_app(
    config_filename: Union[Path, str],
    config_overrides: Optional[Dict[str, Any]] = None,
) -> Flask:
    """Create the actual Flask application."""
    app = Flask(__name__)

    app.config.from_object(config_defaults)
    app.config.from_pyfile(str(config_filename))
    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    # Allow database URI to be overriden via environment variable.
    sqlalchemy_database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if sqlalchemy_database_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_uri

    # Throw an exception when an undefined name is referenced in a template.
    app.jinja_env.undefined = jinja2.StrictUndefined

    # Set the locale.
    set_locale(app.config['LOCALE'])  # Fail if not configured.

    # Initialize database.
    db.init_app(app)

    # Initialize Redis connection.
    redis.init_app(app)

    email.init_app(app)

    config.init_app(app)

    _register_blueprints(app)

    templatefilters.register(app)

    _add_static_file_url_rules(app)

    return app


def _register_blueprints(app: Flask) -> None:
    """Register blueprints depending on the configuration."""
    for name, url_prefix in _get_blueprints(app):
        register_blueprint(app, name, url_prefix)


def _get_blueprints(app: Flask) -> Iterator[BlueprintReg]:
    """Yield blueprints to register on the application."""
    yield from _get_blueprints_common()

    current_mode = config.get_app_mode(app)
    if current_mode.is_site():
        yield from _get_blueprints_site()
    elif current_mode.is_admin():
        yield from _get_blueprints_admin()

    yield from _get_blueprints_api()

    yield from _get_blueprints_health()

    if app.config['METRICS_ENABLED']:
        yield from _get_blueprints_metrics()

    if app.debug:
        yield from _get_blueprints_debug()


def _get_blueprints_common() -> Iterator[BlueprintReg]:
    yield from [
        ('authentication',              '/authentication'           ),
        ('authorization',               None                        ),
        ('core',                        '/core'                     ),
        ('user',                        None                        ),
        ('user.avatar',                 '/users'                    ),
        ('user.creation',               '/users'                    ),
        ('user.current',                '/users'                    ),
        ('user.email_address',          '/users/email_address'      ),
    ]


def _get_blueprints_site() -> Iterator[BlueprintReg]:
    yield from [
        ('attendance',                  '/attendance'               ),
        ('board',                       '/board'                    ),
        ('consent',                     '/consent'                  ),
        ('news',                        '/news'                     ),
        ('newsletter',                  '/newsletter'               ),
        ('orga_team',                   '/orgas'                    ),
        ('party',                       None                        ),
        ('seating',                     '/seating'                  ),
        ('shop.order',                  '/shop'                     ),
        ('shop.orders',                 '/shop/orders'              ),
        ('snippet',                     None                        ),
        ('terms',                       '/terms'                    ),
        ('ticketing',                   '/tickets'                  ),
        ('user.profile',                '/users'                    ),
        ('user_badge',                  '/user_badges'              ),
        ('user_group',                  '/user_groups'              ),
        ('user_message',                '/user_messages'            ),
    ]


def _get_blueprints_admin() -> Iterator[BlueprintReg]:
    yield from [
        ('admin.attendance',            '/admin/attendance'         ),
        ('admin.authorization',         '/admin/authorization'      ),
        ('admin.board',                 '/admin/board'              ),
        ('admin.brand',                 '/admin/brands'             ),
        ('admin.consent',               '/admin/consent'            ),
        ('admin.core',                  None                        ),
        ('admin.dashboard',             '/admin/dashboard'          ),
        ('admin.email',                 '/admin/email'              ),
        ('admin.news',                  '/admin/news'               ),
        ('admin.newsletter',            '/admin/newsletter'         ),
        ('admin.jobs',                  '/admin/jobs'               ),
        ('admin.orga',                  '/admin/orgas'              ),
        ('admin.orga_presence',         '/admin/presence'           ),
        ('admin.orga_team',             '/admin/orga_teams'         ),
        ('admin.party',                 '/admin/parties'            ),
        ('admin.seating',               '/admin/seating'            ),
        ('admin.shop',                  None                        ),
        ('admin.shop.article',          '/admin/shop/articles'      ),
        ('admin.shop.email',            '/admin/shop/email'         ),
        ('admin.shop.order',            '/admin/shop/orders'        ),
        ('admin.shop.shipping',         '/admin/shop/shipping'      ),
        ('admin.shop.shop',             '/admin/shop/shop'          ),
        ('admin.shop.storefront',       '/admin/shop/storefronts'   ),
        ('admin.site',                  '/admin/sites'              ),
        ('admin.snippet',               '/admin/snippets'           ),
        ('admin.terms',                 '/admin/terms'              ),
        ('admin.ticketing',             '/admin/ticketing'          ),
        ('admin.ticketing.checkin',     '/admin/ticketing/checkin'  ),
        ('admin.tourney',               '/admin/tourney'            ),
        ('admin.user',                  '/admin/users'              ),
        ('admin.user_badge',            '/admin/user_badges'        ),
    ]


def _get_blueprints_api() -> Iterator[BlueprintReg]:
    yield from [
        ('api.v1.attendance',               '/api/v1/attendances'       ),
        ('api.v1.snippet',                  '/api/v1/snippets'          ),
        ('api.v1.tourney.avatar',           '/api/v1/tourney/avatars'   ),
        ('api.v1.tourney.match.comments',   '/api/v1/tourney'           ),
        ('api.v1.user',                     '/api/v1/users'             ),
        ('api.v1.user_avatar',              '/api/v1/user_avatars'      ),
        ('api.v1.user_badge',               '/api/v1/user_badges'       ),
    ]


def _get_blueprints_health() -> Iterator[BlueprintReg]:
    yield from [
        ('healthcheck',                 '/health'                   ),
    ]


def _get_blueprints_metrics() -> Iterator[BlueprintReg]:
    yield from [
        ('metrics',                     '/metrics'                  ),
    ]


def _get_blueprints_debug() -> Iterator[BlueprintReg]:
    yield from [
        ('style_guide',                 '/style_guide'              ),
    ]


def _add_static_file_url_rules(app: Flask) -> None:
    """Add URL rules to for static files."""
    app.add_url_rule(
        '/sites/<site_id>/<path:filename>',
        endpoint='site_file',
        methods=['GET'],
        build_only=True,
    )


def init_app(app: Flask) -> None:
    """Initialize the application after is has been created."""
    with app.app_context():
        _set_url_root_path(app)

        app_mode = config.get_app_mode()
        if app_mode.is_site():
            # Incorporate site-specific template overrides.
            app.jinja_loader = SiteTemplateOverridesLoader()

            # Set up site-aware template context processor.
            app._site_context_processors = {}
            app.context_processor(_get_site_template_context)

        _load_announce_signal_handlers()

        if app_mode.is_admin() and app.config['RQ_DASHBOARD_ENABLED']:
            import rq_dashboard
            app.register_blueprint(
                rq_dashboard.blueprint, url_prefix='/admin/rq'
            )


def _set_url_root_path(app: Flask) -> None:
    """Set an optional URL path to redirect to from the root URL path (`/`).

    Important: Don't specify the target with a leading slash unless you
    really mean the root of the host.
    """
    target_url = app.config['ROOT_REDIRECT_TARGET']
    if target_url is None:
        return

    status_code = app.config['ROOT_REDIRECT_STATUS_CODE']

    def _redirect():
        return redirect(target_url, status_code)

    app.add_url_rule('/', endpoint='root', view_func=_redirect)


def _get_site_template_context() -> Dict[str, Any]:
    """Return the site-specific additions to the template context."""
    site_context_processor = _find_site_template_context_processor_cached(
        g.site_id
    )

    if not site_context_processor:
        return {}

    return site_context_processor()


def _find_site_template_context_processor_cached(
    site_id: str
) -> Optional[Callable[[], Dict[str, Any]]]:
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
    site_id: str
) -> Optional[Callable[[], Dict[str, Any]]]:
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
    from .announce import discord
    from .announce.irc import (
        board,
        news,
        shop_order,
        snippet,
        user,
        user_badge,
    )
