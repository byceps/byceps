"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import (
    category_service,
    event_service,
    ticket_creation_service,
    ticket_user_management_service,
)

from tests.conftest import database_recreated
from tests.helpers import create_brand, create_party, create_user


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture(scope='module')
def party():
    brand = create_brand()
    return create_party(brand_id=brand.id)


@pytest.fixture(scope='module')
def category(party):
    return category_service.create_category(party.id, 'Premium')


@pytest.fixture(scope='module')
def ticket_owner(app):
    return create_user('TicketOwner')


@pytest.fixture
def ticket(app, category, ticket_owner):
    return ticket_creation_service.create_ticket(category.id, ticket_owner.id)


def test_appoint_and_withdraw_user_manager(app, ticket, ticket_owner):
    manager = create_user('Ticket_Manager')

    assert ticket.user_managed_by_id is None

    # appoint user manager

    ticket_user_management_service.appoint_user_manager(
        ticket.id, manager.id, ticket_owner.id
    )
    assert ticket.user_managed_by_id == manager.id

    events_after_appointment = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_appointment) == 1

    appointment_event = events_after_appointment[0]
    assert_event(
        appointment_event,
        'user-manager-appointed',
        {
            'appointed_user_manager_id': str(manager.id),
            'initiator_id': str(ticket_owner.id),
        },
    )

    # withdraw user manager

    ticket_user_management_service.withdraw_user_manager(
        ticket.id, ticket_owner.id
    )
    assert ticket.user_managed_by_id is None

    events_after_withdrawal = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_withdrawal) == 2

    withdrawal_event = events_after_withdrawal[1]
    assert_event(
        withdrawal_event,
        'user-manager-withdrawn',
        {'initiator_id': str(ticket_owner.id)},
    )


def test_appoint_and_withdraw_user(app, ticket, ticket_owner):
    user = create_user('Ticket_User')

    assert ticket.used_by_id is None

    # appoint user

    ticket_user_management_service.appoint_user(
        ticket.id, user.id, ticket_owner.id
    )
    assert ticket.used_by_id == user.id

    events_after_appointment = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_appointment) == 1

    appointment_event = events_after_appointment[0]
    assert_event(
        appointment_event,
        'user-appointed',
        {
            'appointed_user_id': str(user.id),
            'initiator_id': str(ticket_owner.id),
        },
    )

    # withdraw user

    ticket_user_management_service.withdraw_user(ticket.id, ticket_owner.id)
    assert ticket.used_by_id is None

    events_after_withdrawal = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_withdrawal) == 2

    withdrawal_event = events_after_withdrawal[1]
    assert_event(
        withdrawal_event,
        'user-withdrawn',
        {'initiator_id': str(ticket_owner.id)},
    )


# helpers


def assert_event(event, event_type, data):
    assert event.event_type == event_type
    assert event.data == data
