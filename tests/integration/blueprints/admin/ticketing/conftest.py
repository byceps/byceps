"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import (
    category_service,
    ticket_bundle_service as bundle_service,
    ticket_creation_service as creation_service,
    ticket_service,
)

from tests.helpers import login_user


@pytest.fixture(scope='package')
def ticketing_admin(make_admin):
    permission_ids = {
        'admin.access',
        'ticketing.administrate_seat_occupancy',
        'ticketing.checkin',
        'ticketing.view',
    }
    admin = make_admin('Ticketing_Admin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def ticketing_admin_client(make_client, admin_app, ticketing_admin):
    return make_client(admin_app, user_id=ticketing_admin.id)


@pytest.fixture(scope='package')
def ticket_owner(make_user):
    return make_user('Ticket_Owner')


@pytest.fixture(scope='package')
def category(party):
    category = category_service.create_category(party.id, 'Basic')

    yield category

    category_service.delete_category(category.id)


@pytest.fixture(scope='package')
def ticket(category, ticket_owner):
    ticket = creation_service.create_ticket(category.id, ticket_owner.id)
    ticket_id = ticket.id

    yield ticket

    ticket_service.delete_ticket(ticket_id)


@pytest.fixture(scope='package')
def bundle(category, ticket_owner):
    quantity = 4
    bundle = bundle_service.create_bundle(
        category.id, quantity, ticket_owner.id
    )
    tickets = bundle.tickets

    yield bundle

    for ticket in tickets:
        ticket_service.delete_ticket(ticket.id)
    bundle_service.delete_bundle(bundle.id)
