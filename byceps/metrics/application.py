"""
byceps.metrics.application
~~~~~~~~~~~~~~~~~~~~~~~~~~

This allows to provide the metrics in a separate application. This might
be desired for performance and/or security reasons.

Run like this (inside a virtual environment)::

    $ DATABASE_URI=your-database-uri-here FLASK_APP=app_metrics flask run --port 8090

Metrics then become available at `http://127.0.0.1/metrics`.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from ..database import db
from ..util.framework.blueprint import get_blueprint


def create_app(database_uri):
    """Create the actual Flask application."""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    # Disable Flask-SQLAlchemy's tracking of object modifications.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database.
    db.init_app(app)

    blueprint = get_blueprint('monitoring.metrics')
    app.register_blueprint(blueprint, url_prefix='/metrics')

    return app
