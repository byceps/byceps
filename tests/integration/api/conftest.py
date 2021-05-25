"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)

API-specific fixtures
"""

import pytest

from .helpers import assemble_authorization_header


API_TOKEN = 'testing-TESTING'


@pytest.fixture(scope='package')
def api_app(admin_app):
    return admin_app


@pytest.fixture(scope='package')
def api_client(api_app):
    """Provide a test HTTP client against the API."""
    return api_app.test_client()


@pytest.fixture(scope='package')
def api_client_authz_header():
    """Provide a test HTTP client against the API."""
    return assemble_authorization_header(API_TOKEN)
