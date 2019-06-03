"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.base import CONFIG_FILENAME_TEST_ADMIN, \
    CONFIG_FILENAME_TEST_PARTY, create_app


@pytest.fixture
def admin_app():
    """Provide the admin web application."""
    app = create_app(CONFIG_FILENAME_TEST_ADMIN)

    with app.app_context():
        yield app


@pytest.fixture
def admin_client(admin_app):
    """Provide a test HTTP client against the admin web application."""
    return admin_app.test_client()


@pytest.fixture
def party_app():
    """Provide a party web application."""
    app = create_app(CONFIG_FILENAME_TEST_PARTY)
    with app.app_context():
        yield app
