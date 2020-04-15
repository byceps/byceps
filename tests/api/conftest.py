"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.

API-specific fixtures
"""

import pytest

from tests.base import create_admin_app
from tests.helpers import create_brand, create_party, provide_user

from ..conftest import CONFIG_PATH_DATA_KEY, database_recreated
from ..helpers import create_site

from .helpers import assemble_authorization_header


API_TOKEN = 'just-say-PLEASE!'


@pytest.fixture(scope='session')
def api_app_without_db(db, data_path):
    config_overrides = {
        'API_TOKEN': API_TOKEN,
        CONFIG_PATH_DATA_KEY: data_path,
    }
    app = create_admin_app(config_overrides)
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def app(api_app_without_db, db):
    app = api_app_without_db
    with database_recreated(db):
        yield app


@pytest.fixture(scope='module')
def site(app, make_email_config):
    make_email_config()
    return create_site()


@pytest.fixture(scope='module')
def party(app):
    brand = create_brand()
    return create_party(brand.id)


@pytest.fixture(scope='module')
def admin_user(app):
    yield from provide_user('AdminForApiTests')


@pytest.fixture(scope='module')
def user(app):
    yield from provide_user('UserForApiTests')


@pytest.fixture(scope='module')
def uninitialized_user(app):
    yield from provide_user('UninitializedUser', initialized=False)


@pytest.fixture(scope='module')
def suspended_user(app):
    yield from provide_user('SuspendedUser', suspended=True)


@pytest.fixture(scope='module')
def deleted_user(app):
    yield from provide_user('DeletedUser', deleted=True)


@pytest.fixture(scope='module')
def api_client(app):
    """Provide a test HTTP client against the API."""
    return app.test_client()


@pytest.fixture(scope='module')
def api_client_authz_header():
    """Provide a test HTTP client against the API."""
    return assemble_authorization_header(API_TOKEN)
