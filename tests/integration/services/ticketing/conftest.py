"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import category_service


@pytest.fixture(scope='package')
def category(party):
    category = category_service.create_category(party.id, 'Premium')
    yield category
    category_service.delete_category(category.id)


@pytest.fixture(scope='package')
def another_category(party):
    category = category_service.create_category(party.id, 'Economy')
    yield category
    category_service.delete_category(category.id)


@pytest.fixture(scope='package')
def ticketing_admin(make_user):
    return make_user('TicketingAdmin')


@pytest.fixture(scope='package')
def ticket_manager(make_user):
    return make_user('TicketManager')


@pytest.fixture(scope='package')
def ticket_owner(make_user):
    return make_user('TicketOwner')
