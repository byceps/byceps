# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

from flask import Flask
import jinja2

from .blueprints.snippet.init import add_routes_for_snippets
from . import config, config_defaults
from .config import SiteMode, STATIC_URL_PREFIX_BRAND, \
    STATIC_URL_PREFIX_GLOBAL, STATIC_URL_PREFIX_PARTY
from .database import db
from . import email
from . import redis
from .util.framework.blueprint import register_blueprint
from .util.l10n import set_locale
from .util import templatefilters


BLUEPRINTS = [
    ('admin_dashboard',     '/admin/dashboard',     SiteMode.admin ),
    ('authentication',      '/authentication',      None           ),
    ('authorization',       None,                   None           ),
    ('authorization_admin', '/admin/authorization', SiteMode.admin ),
    ('board',               '/board',               SiteMode.public),
    ('board_admin',         '/admin/board',         SiteMode.admin ),
    ('brand_admin',         '/admin/brands',        SiteMode.admin ),
    ('core',                '/core',                None           ),
    ('core_admin',          '/admin/core',          SiteMode.admin ),
    ('news',                '/news',                SiteMode.public),
    ('news_admin',          '/admin/news',          SiteMode.admin ),
    ('newsletter',          '/newsletter',          SiteMode.public),
    ('newsletter_admin',    '/admin/newsletter',    SiteMode.admin ),
    ('orga_admin',          '/admin/orgas',         SiteMode.admin ),
    ('orga_presence',       '/admin/presence',      SiteMode.admin ),
    ('orga_team',           '/orgas',               SiteMode.public),
    ('orga_team_admin',     '/admin/orga_teams',    SiteMode.admin ),
    ('party',               None,                   SiteMode.public),
    ('party_admin',         '/admin/parties',       SiteMode.admin ),
    ('seating',             '/seating',             SiteMode.public),
    ('seating_admin',       '/admin/seating',       SiteMode.admin ),
    ('shop_order',          '/shop',                SiteMode.public),
    ('shop_admin',          '/admin/shop',          SiteMode.admin ),
    ('shop_article_admin',  '/admin/shop/articles', SiteMode.admin ),
    ('shop_order_admin',    '/admin/shop/orders',   SiteMode.admin ),
    ('snippet',             '/snippets',            SiteMode.public),
    ('snippet_admin',       '/admin/snippets',      SiteMode.admin ),
    ('terms',               '/terms',               SiteMode.public),
    ('terms_admin',         '/admin/terms',         SiteMode.admin ),
    ('ticketing',           '/tickets',             SiteMode.public),
    ('ticketing_admin',     '/admin/tickets',       SiteMode.admin ),
    ('tourney',             '/tourney',             SiteMode.public),
    ('tourney_admin',       '/admin/tourney',       SiteMode.admin ),
    ('user',                '/users',               None           ),
    ('user_admin',          '/admin/users',         SiteMode.admin ),
    ('user_avatar',         '/users',               None           ),
    ('user_badge',          '/user_badges',         None           ),
    ('user_group',          '/user_groups',         SiteMode.public),
]


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

    redis.init_app(app)

    email.init_app(app)

    config.init_app(app)

    _register_blueprints(app)

    templatefilters.register(app)

    _add_static_file_url_rules(app)

    return app


def _register_blueprints(app):
    """Register the blueprints that are relevant for the current mode."""
    current_mode = config.get_site_mode(app)

    for name, url_prefix, mode in BLUEPRINTS:
        if mode is None or mode == current_mode:
            register_blueprint(app, name, url_prefix)


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
    target = app.config['ROOT_REDIRECT_TARGET']
    if target:
        app.add_url_rule('/', endpoint='root', redirect_to=target)
