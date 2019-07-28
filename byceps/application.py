"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

from flask import Flask, redirect
import jinja2

from .blueprints.snippet.init import add_routes_for_snippets
from . import config, config_defaults
from .database import db
from . import email
from .redis import redis
from .util.framework.blueprint import register_blueprint
from .util.l10n import set_locale
from .util import templatefilters


def create_app(config_filename):
    """Create the actual Flask application."""
    app = Flask(__name__)

    app.config.from_object(config_defaults)
    app.config.from_pyfile(str(config_filename))

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


def _register_blueprints(app):
    """Register blueprints depending on the configuration."""
    for name, url_prefix in _get_blueprints(app):
        register_blueprint(app, name, url_prefix)


def _get_blueprints(app):
    """Yield blueprints to register on the application."""
    yield from [
        ('authentication',          '/authentication'               ),
        ('authorization',           None                            ),
        ('core',                    '/core'                         ),
        ('healthcheck',             '/health'                       ),
        ('user',                    '/users'                        ),
        ('user.creation',           '/users'                        ),
        ('user.email_address',      '/users/email_address'          ),
        ('user.avatar',             '/users'                        ),
    ]

    current_mode = config.get_site_mode(app)
    if current_mode.is_public():
        yield from [
            ('attendance',              '/attendance'               ),
            ('board',                   '/board'                    ),
            ('consent',                 '/consent'                  ),
            ('news',                    '/news'                     ),
            ('newsletter',              '/newsletter'               ),
            ('orga_team',               '/orgas'                    ),
            ('party',                   None                        ),
            ('seating',                 '/seating'                  ),
            ('shop.order',              '/shop'                     ),
            ('shop.orders',             '/shop/orders'              ),
            ('snippet',                 '/snippets'                 ),
            ('terms',                   '/terms'                    ),
            ('ticketing',               '/tickets'                  ),
            ('tourney.avatar',          '/tourney/avatars'          ),
            ('tourney.match',           '/tourney/matches'          ),
            ('user.profile',            '/users'                    ),
            ('user_badge',              '/user_badges'              ),
            ('user_group',              '/user_groups'              ),
            ('user_message',            '/user_messages'            ),
        ]
    elif current_mode.is_admin():
        yield from [
            ('admin_dashboard',         '/admin/dashboard'          ),
            ('admin.authorization',     '/admin/authorization'      ),
            ('admin.board',             '/admin/board'              ),
            ('admin.brand',             '/admin/brands'             ),
            ('admin.consent',           '/admin/consent'            ),
            ('core_admin',              '/admin/core'               ),
            ('admin.news',              '/admin/news'               ),
            ('admin.newsletter',        '/admin/newsletter'         ),
            ('admin.jobs',              '/admin/jobs'               ),
            ('admin.orga',              '/admin/orgas'              ),
            ('admin.orga_presence',     '/admin/presence'           ),
            ('admin.orga_team',         '/admin/orga_teams'         ),
            ('admin.party',             '/admin/parties'            ),
            ('admin.seating',           '/admin/seating'            ),
            ('shop.admin',              None                        ),
            ('shop.article_admin',      '/admin/shop/articles'      ),
            ('shop.email_admin',        '/admin/shop/email'         ),
            ('shop.order_admin',        '/admin/shop/orders'        ),
            ('shop.shipping_admin',     '/admin/shop/shipping'      ),
            ('shop.shop_admin',         '/admin/shop/shop'          ),
            ('admin.site',              '/admin/sites'              ),
            ('admin.snippet',           '/admin/snippets'           ),
            ('admin.terms',             '/admin/terms'              ),
            ('admin.ticketing',         '/admin/ticketing'          ),
            ('ticketing.checkin',       '/admin/ticketing/checkin'  ),
            ('tourney.admin',           '/admin/tourney'            ),
            ('user_admin',              '/admin/users'              ),
            ('user_badge_admin',        '/admin/user_badges'        ),
        ]

    if app.config['METRICS_ENABLED']:
        yield from [
            ('metrics',                 '/metrics'                  ),
        ]

    if app.debug:
        yield from [
            ('style_guide',             '/style_guide'              ),
        ]


def _add_static_file_url_rules(app):
    """Add URL rules to for static files."""
    for rule_prefix, endpoint in [
        (config.STATIC_URL_PREFIX_GLOBAL, 'global_file'),
        (config.STATIC_URL_PREFIX_BRAND, 'brand_file'),
        (config.STATIC_URL_PREFIX_PARTY, 'party_file'),
        (config.STATIC_URL_PREFIX_SITE, 'site_file'),
    ]:
        rule = rule_prefix + '/<path:filename>'
        app.add_url_rule(rule,
                         endpoint=endpoint,
                         methods=['GET'],
                         build_only=True)


def init_app(app):
    """Initialize the application after is has been created."""
    with app.app_context():
        _set_url_root_path(app)

        site_mode = config.get_site_mode()
        if site_mode.is_public():
            # Mount snippets.
            site_id = config.get_current_site_id()
            add_routes_for_snippets(site_id)

            # Incorporate template overrides for the configured site ID.
            site_id = config.get_current_site_id()
            app.template_folder = str(Path('..') / 'sites' / site_id / 'template_overrides')
        elif site_mode.is_admin() and app.config['RQ_DASHBOARD_ENABLED']:
            import rq_dashboard
            app.register_blueprint(rq_dashboard.blueprint,
                                   url_prefix='/admin/rq')


def _set_url_root_path(app):
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
