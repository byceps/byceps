"""
byceps.metrics.application
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import Flask

from ..database import db
from ..util.framework.blueprint import register_blueprint


def create_app(database_uri):
    """Create the actual Flask application."""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    # Disable Flask-SQLAlchemy's tracking of object modifications.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database.
    db.init_app(app)

    register_blueprint(app, 'monitoring.metrics', '/metrics')

    return app
