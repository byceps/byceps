"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

import pytest

from byceps.database import db as _db
from byceps.services.email import service as email_service

from tests.base import (
    CONFIG_FILENAME_TEST_ADMIN,
    CONFIG_FILENAME_TEST_PARTY,
    create_app,
)
from tests.database import set_up_database, tear_down_database
from tests.helpers import create_site, create_user, DEFAULT_EMAIL_CONFIG_ID


@pytest.fixture(scope='session')
def db():
    return _db


@contextmanager
def database_recreated(db):
    set_up_database(db)

    yield

    tear_down_database(db)


@pytest.fixture
def make_admin_app():
    """Provide the admin web application."""

    def _wrapper(**config_overrides):
        return create_app(CONFIG_FILENAME_TEST_ADMIN, config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def admin_app():
    """Provide the admin web application."""
    app = create_app(CONFIG_FILENAME_TEST_ADMIN)
    yield app


@pytest.fixture
def admin_app_with_db(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture
def admin_client(admin_app):
    """Provide a test HTTP client against the admin web application."""
    return admin_app.test_client()


@pytest.fixture(scope='session')
def party_app():
    """Provide a party web application."""
    app = create_app(CONFIG_FILENAME_TEST_PARTY)
    yield app


@pytest.fixture
def party_app_with_db(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            yield party_app


@pytest.fixture
def admin_user():
    return create_user('Admin')


@pytest.fixture
def normal_user():
    return create_user()


@pytest.fixture(scope='session')
def make_email_config():

    def _wrapper():
        config_id = DEFAULT_EMAIL_CONFIG_ID
        sender_address = 'info@shop.example'

        email_service.set_config(config_id, sender_address)

        return email_service.get_config(config_id)

    return _wrapper


@pytest.fixture
def email_config(make_email_config):
    return make_email_config()


@pytest.fixture
def site(email_config):
    return create_site()
