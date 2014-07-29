# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import Flask

from .database import db
from .util import dateformat
from .util.framework import load_config, register_blueprint
from .util.l10n import set_locale


BLUEPRINT_NAMES = [
    ('authorization', '/authorization'),
    ('core', '/core'),
    ('contentpage', '/contentpages'),
    ('user', '/users'),
]


def create_app(config_module_name):
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

    if not app.testing:
        register_content_pages_routes(app)

    return app


def register_content_pages_routes(app):
    """Add URL routes for content pages (which are defined in the database)."""
    from .blueprints.contentpage.views import add_routes_for_pages
    with app.app_context():
        add_routes_for_pages()
