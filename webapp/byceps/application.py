# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import Flask, g

from .blueprints.party.models import Party
from .database import db
from .util import dateformat
from .util.framework import load_config, register_blueprint
from .util.l10n import set_locale


BLUEPRINT_NAMES = [
    ('authorization', '/authorization'),
    ('core', '/core'),
    ('brand', '/brands'),
    ('contentpage', '/contentpages'),
    ('party', '/parties'),
    ('user', '/users'),
]


def create_app(config_module_name, *, initialize=True):
    """Create the actual Flask application."""
    app = Flask(__name__)

    # Load configuration from file.
    load_config(app, config_module_name)

    # Set the locale.
    set_locale(app.config['LOCALE'])  # Fail if not configured.

    # Initialize database.
    db.init_app(app)

    # Import and register blueprints.
    for name, url_prefix in BLUEPRINT_NAMES:
        register_blueprint(app, name, url_prefix)

    dateformat.register_template_filters(app)

    if initialize:
        with app.app_context():
            g.party = get_current_party(app)
            register_content_pages_routes()

    return app


def get_current_party(app):
    """Determine the current party from the configuration."""
    party_id = app.config.get('PARTY')
    if party_id is None:
        raise Exception('No party configured.')

    party = Party.query.get(party_id)
    if party is None:
        raise Exception('Unknown party "{}".'.format(party_id))

    return party


def register_content_pages_routes():
    """Add URL routes for content pages (which are defined in the database)."""
    from .blueprints.contentpage.views import add_routes_for_pages
    add_routes_for_pages()
