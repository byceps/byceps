# -*- coding: utf-8 -*-

from contextlib import contextmanager
from itertools import count, islice
import os

from byceps.application import create_app
from byceps.database import db
from byceps.util.system import get_config_env_name_from_env


get_config_name_from_env = get_config_env_name_from_env


@contextmanager
def app_context(config_name):
    """Provide a context in which the application is available with the
    specified environment.
    """
    app = create_app(config_name, initialize=False)
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
