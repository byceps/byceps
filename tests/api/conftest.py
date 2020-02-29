"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.

API-specific fixtures
"""

import pytest

from tests.base import CONFIG_FILENAME_TEST_ADMIN, create_app
from tests.helpers import create_brand, create_party, create_user

from ..conftest import database_recreated
from ..helpers import create_email_config, create_site

from .helpers import assemble_authorization_header


API_TOKEN = 'just-say-PLEASE!'


@pytest.fixture(scope='session')
def api_app_without_db(db):
    app = create_app(CONFIG_FILENAME_TEST_ADMIN, {'API_TOKEN': API_TOKEN})
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def app(api_app_without_db, db):
    app = api_app_without_db
    with database_recreated(db):
        yield app


@pytest.fixture(scope='module')
def site(app):
    create_email_config()
    return create_site()


@pytest.fixture(scope='module')
def party(app):
    brand = create_brand()
    return create_party(brand.id)


@pytest.fixture(scope='module')
def admin(app):
    return create_user('Admin')


@pytest.fixture(scope='module')
def user(app):
    return create_user('User')


@pytest.fixture(scope='module')
def uninitialized_user(app):
    return create_user('UninitializedUser', initialized=False)


@pytest.fixture(scope='module')
def suspended_user(app):
    return create_user('SuspendedUser', suspended=True)


@pytest.fixture(scope='module')
def deleted_user(app):
    return create_user('DeletedUser', deleted=True)


@pytest.fixture(scope='module')
def api_client(app):
    """Provide a test HTTP client against the API."""
    return app.test_client()


@pytest.fixture(scope='module')
def api_client_authz_header():
    """Provide a test HTTP client against the API."""
    return assemble_authorization_header(API_TOKEN)
