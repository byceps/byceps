"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.party import service as party_service
from byceps.services.ticketing import category_service

from tests.helpers import create_brand, create_party, create_user


@pytest.fixture(scope='module')
def brand(admin_app_with_db):
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


@pytest.fixture(scope='module')
def party(brand):
    party = create_party(brand.id)
    yield party
    party_service.delete_party(party.id)


@pytest.fixture(scope='module')
def category(party):
    category = category_service.create_category(party.id, 'Premium')
    yield category
    category_service.delete_category(category.id)


@pytest.fixture(scope='module')
def another_category(party):
    category = category_service.create_category(party.id, 'Economy')
    yield category
    category_service.delete_category(category.id)


@pytest.fixture(scope='module')
def ticketing_admin(admin_app_with_db):
    return create_user('TicketingAdmin')


@pytest.fixture(scope='module')
def ticket_manager(admin_app_with_db):
    return create_user('TicketManager')


@pytest.fixture(scope='module')
def ticket_owner(admin_app_with_db):
    return create_user('TicketOwner')


@pytest.fixture(scope='module')
def ticket_user(admin_app_with_db):
    return create_user('TicketUser')
