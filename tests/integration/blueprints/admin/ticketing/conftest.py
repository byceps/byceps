"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import (
    ticket_bundle_service,
    ticket_category_service,
    ticket_creation_service,
)

from tests.helpers import generate_token, log_in_user


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
    title = generate_token()
    return ticket_category_service.create_category(party.id, title)


@pytest.fixture(scope='package')
def ticket(category, ticket_owner):
    return ticket_creation_service.create_ticket(category, ticket_owner)


@pytest.fixture(scope='package')
def bundle(category, ticket_owner, *, quantity=4):
    return ticket_bundle_service.create_bundle(category, quantity, ticket_owner)
