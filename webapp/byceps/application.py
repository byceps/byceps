# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
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
from .util import dateformat
from .util.framework import load_config, register_blueprint
from .util.l10n import set_locale
from .util import money


BLUEPRINTS = [
    ('authorization',       '/authorization',       None           ),
    ('authorization_admin', '/admin/authorization', SiteMode.admin ),
    ('board',               '/board',               SiteMode.public),
    ('board_admin',         '/admin/board',         SiteMode.admin ),
    #('brand',               None,                   None           ),
    ('core',                '/core',                None           ),
    ('news',                '/news',                SiteMode.public),
    ('news_admin',          '/admin/news',          SiteMode.admin ),
    ('newsletter',          '/newsletter',          None           ),
    ('newsletter_admin',    '/admin/newsletter',    SiteMode.admin ),
    ('orga',                '/orgas',               SiteMode.public),
    ('orga_admin',          '/admin/orgas',         SiteMode.admin ),
    ('orga_presence',       '/admin/presence',      SiteMode.admin ),
    ('party',               None,                   SiteMode.public),
    ('party_admin',         '/admin/parties',       SiteMode.admin ),
    ('seating',             '/seating',             SiteMode.public),
    ('shop',                '/shop',                SiteMode.public),
    ('shop_admin',          '/admin/shop',          SiteMode.admin ),
    ('snippet',             '/snippets',            None           ),
    ('snippet_admin',       '/admin/snippets',      SiteMode.admin ),
    ('terms',               '/terms',               SiteMode.public),
    ('terms_admin',         '/admin/terms',         SiteMode.admin ),
    ('ticket',              '/tickets',             SiteMode.public),
    ('ticket_admin',        '/admin/tickets',       SiteMode.admin ),
    ('tourney',             '/tourney',             SiteMode.public),
    ('user',                '/users',               None           ),
    ('user_admin',          '/admin/users',         SiteMode.admin ),
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

    # Initialize database.
    db.init_app(app)

    redis.init_app(app)

    email.init_app(app)

    config.init_app(app)

    register_blueprints(app)

    dateformat.register_template_filters(app)
    money.register_template_filters(app)

    app.add_url_rule('/content/<path:filename>',
                     endpoint='content_file',
                     methods=['GET'],
                     build_only=True)

    app.add_url_rule('/content/brand/<path:filename>',
                     endpoint='brand_file',
                     build_only=True)

    return app


def register_blueprints(app):
    """Register the blueprints that are relevant for the current mode."""
    current_mode = config.get_site_mode(app)

    for name, url_prefix, mode in BLUEPRINTS:
        if mode is None or mode == current_mode:
            register_blueprint(app, name, url_prefix)


def init_app(app):
    """Initialize the application after is has been created."""
    with app.app_context():
        set_root_path(app)

        site_mode = config.get_site_mode()
        if site_mode.is_public():
            party_id = config.get_current_party_id()

            # Mount snippets.
            add_routes_for_snippets(party_id)

            # Incorporate template overrides for the current party.
            app.template_folder = str(Path('party_template_overrides') \
                                / party_id)
        elif site_mode.is_admin():
            from rq_dashboard import RQDashboard
            RQDashboard(app, url_prefix='/admin/rq')


def set_root_path(app):
    """Set an optional URL path to redirect to from the root URL path (`/`).

    Important: Don't specify the target with a leading slash unless you
    really mean the root of the host.
    """
    target = app.config.get('ROOT_REDIRECT_TARGET')
    if target:
        app.add_url_rule('/', endpoint='root', redirect_to=target)
