"""
bootstrap.util
~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager
from itertools import count, islice

from byceps.application import create_app
from byceps.database import db


@contextmanager
def app_context(config_filename):
    """Provide a context in which the application is available with the
    specified configuration.
    """
    app = create_app(config_filename)
    with app.app_context():
        yield app


def add_to_database(f):
    def decorated(*args, **kwargs):
        entity = f(*args, **kwargs)
        db.session.add(entity)
        return entity
    return decorated


def add_all_to_database(f):
    def decorated(*args, **kwargs):
        entities = f(*args, **kwargs)
        for entity in entities:
            db.session.add(entity)
        return entities
    return decorated


def generate_positive_numbers(n):
    """Generate a sequence of `n` positive, consecutive numbers."""
    return islice(count(1), n)
