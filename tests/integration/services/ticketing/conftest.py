"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import category_service


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
def ticketing_admin(make_user):
    return make_user('TicketingAdmin')


@pytest.fixture(scope='module')
def ticket_manager(make_user):
    return make_user('TicketManager')


@pytest.fixture(scope='module')
def ticket_owner(make_user):
    return make_user('TicketOwner')
