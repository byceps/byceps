# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

from flask import Flask
import jinja2
from pytz import timezone

from .blueprints.snippet.init import add_routes_for_snippets
from . import config
from .config import SiteMode
from .database import db
from . import email
from . import redis
from .util.framework.blueprint import register_blueprint
from .util.framework.config import load_config
from .util.l10n import set_locale
from .util import templatefilters


BLUEPRINTS = [
    ('admin_dashboard',     '/admin/dashboard',     SiteMode.admin ),
    ('authentication',      '/authentication',      None           ),
    ('authorization',       None,                   None           ),
    ('authorization_admin', '/admin/authorization', SiteMode.admin ),
    ('board',               '/board',               SiteMode.public),
    ('board_admin',         '/admin/board',         SiteMode.admin ),
    #('brand',               None,                   None           ),
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
    ('ticket',              '/tickets',             SiteMode.public),
    ('ticket_admin',        '/admin/tickets',       SiteMode.admin ),
    ('tourney',             '/tourney',             SiteMode.public),
    ('tourney_admin',       '/admin/tourney',       SiteMode.admin ),
    ('user',                '/users',               None           ),
    ('user_admin',          '/admin/users',         SiteMode.admin ),
    ('user_avatar',         '/users',               None           ),
    ('user_badge',          '/user_badges',         None           ),
    ('user_group',          '/user_groups',         SiteMode.public),
]

TIMEZONE = timezone('Europe/Berlin')


def create_app(environment_name):
    """Create the actual Flask application."""
    app = Flask(__name__)

    load_config(app, environment_name)

    # Throw an exception when an undefined name is referenced in a template.
    app.jinja_env.undefined = jinja2.StrictUndefined

    # Set the locale.
    set_locale(app.config['LOCALE'])  # Fail if not configured.

    # Add the time zone to the configuration.
    app.config['TIMEZONE'] = TIMEZONE

    # Disable Flask-SQLAlchemy's tracking of object modifications.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    for rule, endpoint in [
        ('/global/<path:filename>', 'global_file'),
        ('/brand/<path:filename>', 'brand_file'),
        ('/party/<path:filename>', 'party_file'),
    ]:
        app.add_url_rule(rule,
                         endpoint=endpoint,
                         methods=['GET'],
                         build_only=True)


def init_app(app):
    """Initialize the application after is has been created."""
    with app.app_context():
        _set_root_path(app)

        site_mode = config.get_site_mode()
        if site_mode.is_public():
            party_id = config.get_current_party_id()

            # Mount snippets.
            add_routes_for_snippets(party_id)

            # Incorporate template overrides for the current party.
            app.template_folder = str(Path('party_template_overrides') \
                                / party_id)
        elif site_mode.is_admin():
            import rq_dashboard
            _add_to_config_if_not_set(app, 'RQ_POLL_INTERVAL', 2500)
            app.register_blueprint(rq_dashboard.blueprint,
                                   url_prefix='/admin/rq')


def _set_root_path(app):
    """Set an optional URL path to redirect to from the root URL path (`/`).

    Important: Don't specify the target with a leading slash unless you
    really mean the root of the host.
    """
    target = app.config.get('ROOT_REDIRECT_TARGET')
    if target:
        app.add_url_rule('/', endpoint='root', redirect_to=target)


def _add_to_config_if_not_set(app, key, value):
    """Add the value to the configuration if the key is not yet contained."""
    if key not in app.config:
        app.config[key] = value
