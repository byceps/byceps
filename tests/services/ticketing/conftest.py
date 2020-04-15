"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import category_service

from tests.conftest import database_recreated
from tests.helpers import create_brand, create_party, create_user


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture(scope='module')
def brand(app):
    return create_brand()


@pytest.fixture(scope='module')
def party(brand):
    return create_party(brand_id=brand.id)


@pytest.fixture(scope='module')
def category(party):
    return category_service.create_category(party.id, 'Premium')


@pytest.fixture(scope='module')
def another_category(party):
    return category_service.create_category(party.id, 'Economy')


@pytest.fixture(scope='module')
def ticketing_admin(app):
    return create_user('TicketingAdmin')


@pytest.fixture(scope='module')
def ticket_manager(app):
    return create_user('TicketManager')


@pytest.fixture(scope='module')
def ticket_owner(app):
    return create_user('TicketOwner')


@pytest.fixture(scope='module')
def ticket_user(app):
    return create_user('TicketUser')
