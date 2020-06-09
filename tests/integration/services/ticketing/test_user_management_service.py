"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import (
    event_service,
    ticket_creation_service,
    ticket_service,
    ticket_user_management_service,
)


@pytest.fixture
def ticket(admin_app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(category.id, ticket_owner.id)
    yield ticket
    ticket_service.delete_ticket(ticket.id)


def test_appoint_and_withdraw_user_manager(admin_app, ticket, ticket_manager):
    assert ticket.user_managed_by_id is None

    # appoint user manager

    ticket_user_management_service.appoint_user_manager(
        ticket.id, ticket_manager.id, ticket.owned_by_id
    )
    assert ticket.user_managed_by_id == ticket_manager.id

    events_after_appointment = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_appointment) == 1

    appointment_event = events_after_appointment[0]
    assert_event(
        appointment_event,
        'user-manager-appointed',
        {
            'appointed_user_manager_id': str(ticket_manager.id),
            'initiator_id': str(ticket.owned_by_id),
        },
    )

    # withdraw user manager

    ticket_user_management_service.withdraw_user_manager(
        ticket.id, ticket.owned_by_id
    )
    assert ticket.user_managed_by_id is None

    events_after_withdrawal = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_withdrawal) == 2

    withdrawal_event = events_after_withdrawal[1]
    assert_event(
        withdrawal_event,
        'user-manager-withdrawn',
        {'initiator_id': str(ticket.owned_by_id)},
    )


def test_appoint_and_withdraw_user(admin_app, ticket, make_user):
    ticket_user = make_user('TicketUserToAppointAndWithdraw')

    assert ticket.used_by_id is None

    # appoint user

    ticket_user_management_service.appoint_user(
        ticket.id, ticket_user.id, ticket.owned_by_id
    )
    assert ticket.used_by_id == ticket_user.id

    events_after_appointment = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_appointment) == 1

    appointment_event = events_after_appointment[0]
    assert_event(
        appointment_event,
        'user-appointed',
        {
            'appointed_user_id': str(ticket_user.id),
            'initiator_id': str(ticket.owned_by_id),
        },
    )

    # withdraw user

    ticket_user_management_service.withdraw_user(ticket.id, ticket.owned_by_id)
    assert ticket.used_by_id is None

    events_after_withdrawal = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_withdrawal) == 2

    withdrawal_event = events_after_withdrawal[1]
    assert_event(
        withdrawal_event,
        'user-withdrawn',
        {'initiator_id': str(ticket.owned_by_id)},
    )


# helpers


def assert_event(event, event_type, data):
    assert event.event_type == event_type
    assert event.data == data
