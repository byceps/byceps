"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import (
    ticket_bundle_service,
    ticket_category_service,
    ticket_creation_service,
    ticket_service,
)

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def ticketing_admin(make_admin):
    permission_ids = {
        'admin.access',
        'ticketing.administrate',
        'ticketing.administrate_seat_occupancy',
        'ticketing.checkin',
        'ticketing.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def ticketing_admin_client(make_client, admin_app, ticketing_admin):
    return make_client(admin_app, user_id=ticketing_admin.id)


@pytest.fixture(scope='package')
def ticket_owner(make_user):
    return make_user()


@pytest.fixture(scope='package')
def category(party):
    category = ticket_category_service.create_category(party.id, 'Basic')

    yield category

    ticket_category_service.delete_category(category.id)


@pytest.fixture(scope='package')
def ticket(category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )
    ticket_id = ticket.id

    yield ticket

    ticket_service.delete_ticket(ticket_id)


@pytest.fixture(scope='package')
def bundle(category, ticket_owner):
    quantity = 4
    bundle = ticket_bundle_service.create_bundle(
        category.party_id, category.id, quantity, ticket_owner.id
    )
    tickets = bundle.tickets

    yield bundle

    for ticket in tickets:
        ticket_service.delete_ticket(ticket.id)
    ticket_bundle_service.delete_bundle(bundle.id)
