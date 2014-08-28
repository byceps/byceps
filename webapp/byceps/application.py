# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import Flask, g
import jinja2

from .blueprints.snippet.init import add_routes_for_snippets
from .database import db
from .util import dateformat
from .util.framework import load_config, register_blueprint
from .util.l10n import set_locale


BLUEPRINT_NAMES = [
    ('authorization', '/authorization'),
    ('board', '/board'),
    ('brand', '/brands'),
    ('core', '/core'),
    ('orga', '/orgas'),
    ('orga_admin', '/orgas/admin'),
    ('party', None),
    ('party_admin', '/parties'),
    ('seating', '/seating'),
    ('snippet', '/snippets'),
    ('snippet_admin', '/snippets'),
    ('terms', '/terms'),
    ('terms_admin', '/terms/admin'),
    ('user', '/users'),
    ('user_admin', '/users'),
]


def create_app(environment_name, *, initialize=True):
    """Create the actual Flask application."""
    app = Flask(__name__)

    load_config(app, environment_name)

    # Throw an exception when an undefined name is referenced in a template.
    app.jinja_env.undefined = jinja2.StrictUndefined

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
            app.party_id = get_current_party_id(app)
            add_routes_for_snippets()

    return app


def get_current_party_id(app):
    """Determine the current party from the configuration."""
    party_id = app.config.get('PARTY')
    if party_id is None:
        raise Exception('No party configured.')

    return party_id
