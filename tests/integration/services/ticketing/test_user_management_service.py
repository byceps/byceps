"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import (
    ticket_creation_service,
    ticket_log_service,
    ticket_service,
    ticket_user_management_service,
)


@pytest.fixture
def ticket(admin_app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )
    yield ticket
    ticket_service.delete_ticket(ticket.id)


def test_appoint_and_withdraw_user_manager(admin_app, ticket, ticket_manager):
    assert ticket.user_managed_by_id is None

    # appoint user manager

    ticket_user_management_service.appoint_user_manager(
        ticket.id, ticket_manager.id, ticket.owned_by_id
    )
    assert ticket.user_managed_by_id == ticket_manager.id

    log_entries_after_appointment = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_appointment) == 1

    appointment_log_entry = log_entries_after_appointment[0]
    assert_log_entry(
        appointment_log_entry,
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

    log_entries_after_withdrawal = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_withdrawal) == 2

    withdrawal_log_entry = log_entries_after_withdrawal[1]
    assert_log_entry(
        withdrawal_log_entry,
        'user-manager-withdrawn',
        {'initiator_id': str(ticket.owned_by_id)},
    )


def test_appoint_and_withdraw_user(admin_app, ticket, make_user):
    ticket_user = make_user()

    assert ticket.used_by_id is None

    # appoint user

    ticket_user_management_service.appoint_user(
        ticket.id, ticket_user.id, ticket.owned_by_id
    )
    assert ticket.used_by_id == ticket_user.id

    log_entries_after_appointment = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_appointment) == 1

    appointment_log_entry = log_entries_after_appointment[0]
    assert_log_entry(
        appointment_log_entry,
        'user-appointed',
        {
            'appointed_user_id': str(ticket_user.id),
            'initiator_id': str(ticket.owned_by_id),
        },
    )

    # withdraw user

    ticket_user_management_service.withdraw_user(ticket.id, ticket.owned_by_id)
    assert ticket.used_by_id is None

    log_entries_after_withdrawal = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_withdrawal) == 2

    withdrawal_log_entry = log_entries_after_withdrawal[1]
    assert_log_entry(
        withdrawal_log_entry,
        'user-withdrawn',
        {'initiator_id': str(ticket.owned_by_id)},
    )


# helpers


def assert_log_entry(log_entry, event_type, data):
    assert log_entry.event_type == event_type
    assert log_entry.data == data
