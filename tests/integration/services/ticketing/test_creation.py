"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

from pytest import raises

from byceps.services.ticketing import (
    log_service,
    ticket_code_service,
    ticket_creation_service,
)


def test_create_ticket(admin_app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )

    assert_created_ticket(ticket, category.id, ticket_owner.id)


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_ticket_with_existing_code(
    generate_ticket_code_mock, admin_app, category, ticket_owner
):
    generate_ticket_code_mock.return_value = 'TAKEN'

    existing_ticket = ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )
    assert existing_ticket.code == 'TAKEN'

    with raises(ticket_creation_service.TicketCreationFailedWithConflict):
        ticket_creation_service.create_ticket(
            category.party_id, category.id, ticket_owner.id
        )


def test_create_tickets(admin_app, category, ticket_owner):
    quantity = 3
    tickets = ticket_creation_service.create_tickets(
        category.party_id, category.id, ticket_owner.id, quantity
    )

    for ticket in tickets:
        assert_created_ticket(ticket, category.id, ticket_owner.id)


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_clashing_generated_codes(
    generate_ticket_code_mock, admin_app, category, ticket_owner
):
    generate_ticket_code_mock.return_value = 'CLASH'

    quantity = 3

    with raises(ticket_creation_service.TicketCreationFailed) as excinfo:
        ticket_creation_service.create_tickets(
            category.party_id, category.id, ticket_owner.id, quantity
        )

    wrapped_exc = excinfo.value.args[0]
    assert type(wrapped_exc) is ticket_code_service.TicketCodeGenerationFailed


def assert_created_ticket(ticket, expected_category_id, expected_owner_id):
    assert ticket is not None
    assert ticket.created_at is not None
    assert ticket.code is not None
    assert ticket.bundle_id is None
    assert ticket.category_id == expected_category_id
    assert ticket.owned_by_id == expected_owner_id
    assert ticket.seat_managed_by_id is None
    assert ticket.user_managed_by_id is None
    assert ticket.occupied_seat_id is None
    assert ticket.used_by_id is None
    assert not ticket.revoked
    assert not ticket.user_checked_in

    log_entries = log_service.get_entries_for_ticket(ticket.id)
    assert len(log_entries) == 0
