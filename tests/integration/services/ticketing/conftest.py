"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest


@pytest.fixture(scope='package')
def category(make_ticket_category, party):
    return make_ticket_category(party.id, 'Premium')


@pytest.fixture(scope='package')
def another_category(make_ticket_category, party):
    return make_ticket_category(party.id, 'Economy')


@pytest.fixture(scope='package')
def ticketing_admin(make_user):
    return make_user('TicketingAdmin')


@pytest.fixture(scope='package')
def ticket_manager(make_user):
    return make_user('TicketManager')


@pytest.fixture(scope='package')
def ticket_owner(make_user):
    return make_user('TicketOwner')
