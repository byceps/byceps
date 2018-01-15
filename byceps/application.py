"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

from flask import Flask, redirect
import jinja2

from .blueprints.snippet.init import add_routes_for_snippets
from . import config, config_defaults
from .config import STATIC_URL_PREFIX_BRAND, STATIC_URL_PREFIX_GLOBAL, \
    STATIC_URL_PREFIX_PARTY
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
    current_mode = config.get_site_mode(app)

    always = True
    debug = app.debug
    site_mode_admin = current_mode.is_admin()
    site_mode_public = current_mode.is_public()

    blueprints = [
        ('admin_dashboard',         '/admin/dashboard',         site_mode_admin     ),
        ('attendance',              '/attendance',              site_mode_public    ),
        ('authentication',          '/authentication',          always              ),
        ('authorization',           None,                       always              ),
        ('authorization_admin',     '/admin/authorization',     site_mode_admin     ),
        ('board',                   '/board',                   site_mode_public    ),
        ('board_admin',             '/admin/board',             site_mode_admin     ),
        ('brand_admin',             '/admin/brands',            site_mode_admin     ),
        ('core',                    '/core',                    always              ),
        ('core_admin',              '/admin/core',              site_mode_admin     ),
        ('news',                    '/news',                    site_mode_public    ),
        ('news_admin',              '/admin/news',              site_mode_admin     ),
        ('newsletter',              '/newsletter',              site_mode_public    ),
        ('newsletter_admin',        '/admin/newsletter',        site_mode_admin     ),
        ('orga_admin',              '/admin/orgas',             site_mode_admin     ),
        ('orga_presence',           '/admin/presence',          site_mode_admin     ),
        ('orga_team',               '/orgas',                   site_mode_public    ),
        ('orga_team_admin',         '/admin/orga_teams',        site_mode_admin     ),
        ('party',                   None,                       site_mode_public    ),
        ('party_admin',             '/admin/parties',           site_mode_admin     ),
        ('seating',                 '/seating',                 site_mode_public    ),
        ('seating_admin',           '/admin/seating',           site_mode_admin     ),
        ('shop.admin',              '/admin/shop',              site_mode_admin     ),
        ('shop.orders',             '/shop/orders',             site_mode_public    ),
        ('shop_order',              '/shop',                    site_mode_public    ),
        ('shop_article_admin',      '/admin/shop/articles',     site_mode_admin     ),
        ('shop_order_admin',        '/admin/shop/orders',       site_mode_admin     ),
        ('snippet',                 '/snippets',                site_mode_public    ),
        ('snippet_admin',           '/admin/snippets',          site_mode_admin     ),
        ('style_guide',             '/style_guide',             debug               ),
        ('terms',                   '/terms',                   site_mode_public    ),
        ('terms_admin',             '/admin/terms',             site_mode_admin     ),
        ('ticketing',               '/tickets',                 site_mode_public    ),
        ('ticketing_admin',         '/admin/ticketing',         site_mode_admin     ),
        ('ticketing.checkin',       '/admin/ticketing/checkin', site_mode_admin     ),
        ('tourney',                 '/tourney',                 site_mode_public    ),
        ('tourney_admin',           '/admin/tourney',           site_mode_admin     ),
        ('tourney.avatar',          '/tourney/avatars',         site_mode_public    ),
        ('user',                    '/users',                   always              ),
        ('user_admin',              '/admin/users',             site_mode_admin     ),
        ('user_avatar',             '/users',                   always              ),
        ('user_badge',              '/user_badges',             site_mode_public    ),
        ('user_badge_admin',        '/user_badges/admin',       site_mode_admin     ),
        ('user_group',              '/user_groups',             site_mode_public    ),
    ]

    for name, url_prefix, include in blueprints:
        if include:
            yield name, url_prefix


def _add_static_file_url_rules(app):
    """Add URL rules to for static files."""
    for rule_prefix, endpoint in [
        (STATIC_URL_PREFIX_GLOBAL, 'global_file'),
        (STATIC_URL_PREFIX_BRAND, 'brand_file'),
        (STATIC_URL_PREFIX_PARTY, 'party_file'),
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
            party_id = config.get_current_party_id()

            # Mount snippets.
            add_routes_for_snippets(party_id)

            # Incorporate template overrides for the current party.
            app.template_folder = str(Path('party_template_overrides') \
                                / party_id)
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
