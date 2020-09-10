"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing import (
    event_service,
    ticket_creation_service,
    ticket_service,
)


def test_create_ticket(admin_app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(category.id, ticket_owner.id)

    assert_created_ticket(ticket, category.id, ticket_owner.id)

    # Clean up.
    ticket_service.delete_ticket(ticket.id)


def test_create_tickets(admin_app, category, ticket_owner):
    quantity = 3
    tickets = ticket_creation_service.create_tickets(
        category.id, ticket_owner.id, quantity
    )

    for ticket in tickets:
        assert_created_ticket(ticket, category.id, ticket_owner.id)

    # Clean up.
    for ticket in tickets:
        ticket_service.delete_ticket(ticket.id)


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

    events = event_service.get_events_for_ticket(ticket.id)
    assert len(events) == 0
