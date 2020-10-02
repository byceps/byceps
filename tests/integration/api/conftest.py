"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.

API-specific fixtures
"""

import pytest

from tests.base import create_admin_app
from tests.conftest import CONFIG_PATH_DATA_KEY

from .helpers import assemble_authorization_header


API_TOKEN = 'just-say-PLEASE!'


@pytest.fixture(scope='session')
# `admin_app` fixture is required because it sets up the database.
def api_app(admin_app, make_admin_app):
    config_overrides = {
        'API_TOKEN': API_TOKEN,
        'SERVER_NAME': 'api.acmecon.test',
    }
    app = make_admin_app(**config_overrides)
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def api_client(api_app):
    """Provide a test HTTP client against the API."""
    return api_app.test_client()


@pytest.fixture(scope='session')
def api_client_authz_header():
    """Provide a test HTTP client against the API."""
    return assemble_authorization_header(API_TOKEN)
