"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.

Fixtures specific to admin blueprints
"""

import pytest

from tests.conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    app = admin_app
    with app.app_context():
        with database_recreated(db):
            yield app
