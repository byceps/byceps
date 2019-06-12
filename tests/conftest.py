"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.database import db

from tests.base import CONFIG_FILENAME_TEST_ADMIN, \
    CONFIG_FILENAME_TEST_PARTY, create_app


@pytest.fixture(scope='session')
def admin_app():
    """Provide the admin web application."""
    app = create_app(CONFIG_FILENAME_TEST_ADMIN)
    yield app


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
def party_app_with_db(party_app):
    with party_app.app_context():
        db.reflect()
        db.drop_all()

        db.create_all()

        yield party_app

        db.session.remove()
