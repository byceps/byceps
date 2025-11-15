"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.seating import seat_service, seating_area_service

# Import models to ensure the corresponding tables are created so
# `Seat.assignment` is available.
import byceps.services.seating.dbmodels.seat_group  # noqa: F401
from byceps.services.ticketing import (
    ticket_creation_service,
    ticket_log_service,
    ticket_revocation_service,
    ticket_seat_management_service,
    ticket_service,
)

from tests.helpers import generate_token


@pytest.fixture(scope='module')
def area(party):
    token = generate_token()
    return seating_area_service.create_area(party.id, token, token)


@pytest.fixture()
def ticket(category, ticket_owner):
    return ticket_creation_service.create_ticket(category, ticket_owner)


@pytest.fixture()
def tickets(category, ticket_owner, *, quantity=3):
    return ticket_creation_service.create_tickets(
        category, ticket_owner, quantity
    )


@pytest.fixture()
def seat(area, category):
    return seat_service.create_seat(area.id, 0, 0, category.id)


@pytest.fixture()
def seats(tickets, area):
    return [
        seat_service.create_seat(area.id, 0, 0, ticket.category_id)
        for ticket in tickets
    ]


def test_revoke_ticket(admin_app, ticket, ticketing_admin):
    ticket_before = ticket
    assert not ticket_before.revoked

    log_entries_before = ticket_log_service.get_entries_for_ticket(
        ticket_before.id
    )
    assert len(log_entries_before) == 0

    # -------------------------------- #

    ticket_id = ticket_before.id

    ticket_revocation_service.revoke_ticket(ticket_id, ticketing_admin)

    # -------------------------------- #

    ticket_after = ticket_service.get_ticket(ticket_id)
    assert ticket_after.revoked

    log_entries_after = ticket_log_service.get_entries_for_ticket(
        ticket_after.id
    )
    assert len(log_entries_after) == 1

    ticket_revoked_log_entry = log_entries_after[0]
    assert ticket_revoked_log_entry.event_type == 'ticket-revoked'
    assert ticket_revoked_log_entry.data == {
        'initiator_id': str(ticketing_admin.id)
    }


def test_revoke_tickets(admin_app, tickets, ticketing_admin):
    tickets_before = tickets

    for ticket_before in tickets_before:
        assert not ticket_before.revoked

        log_entries_before = ticket_log_service.get_entries_for_ticket(
            ticket_before.id
        )
        assert len(log_entries_before) == 0

    # -------------------------------- #

    ticket_ids = {ticket.id for ticket in tickets_before}

    ticket_revocation_service.revoke_tickets(ticket_ids, ticketing_admin)

    # -------------------------------- #

    tickets_after = ticket_service.get_tickets(ticket_ids)
    for ticket_after in tickets_after:
        assert ticket_after.revoked

        log_entries_after = ticket_log_service.get_entries_for_ticket(
            ticket_after.id
        )
        assert len(log_entries_after) == 1

        ticket_revoked_log_entry = log_entries_after[0]
        assert ticket_revoked_log_entry.event_type == 'ticket-revoked'
        assert ticket_revoked_log_entry.data == {
            'initiator_id': str(ticketing_admin.id)
        }


def test_revoke_ticket_with_seat(
    admin_app, area, ticket_owner, ticket, ticketing_admin, seat
):
    ticket_seat_management_service.occupy_seat(
        ticket.id, seat.id, ticket_owner
    ).unwrap()

    assert ticket.occupied_seat_id == seat.id

    log_entries_before = ticket_log_service.get_entries_for_ticket(ticket.id)
    event_types_before = {entry.event_type for entry in log_entries_before}
    assert 'seat-released' not in event_types_before

    # -------------------------------- #

    ticket_revocation_service.revoke_ticket(ticket.id, ticketing_admin)

    # -------------------------------- #

    assert ticket.occupied_seat_id is None

    log_entries_after = ticket_log_service.get_entries_for_ticket(ticket.id)
    event_types_after = {entry.event_type for entry in log_entries_after}
    assert 'seat-released' in event_types_after


def test_revoke_tickets_with_seats(
    admin_app, area, ticket_owner, tickets, ticketing_admin, seats
):
    ticket_ids = {ticket.id for ticket in tickets}

    for ticket, seat in zip(tickets, seats, strict=True):
        ticket_seat_management_service.occupy_seat(
            ticket.id, seat.id, ticket_owner
        ).unwrap()

        assert ticket.occupied_seat_id == seat.id

    # -------------------------------- #

    ticket_revocation_service.revoke_tickets(ticket_ids, ticketing_admin)

    # -------------------------------- #

    for ticket in tickets:
        assert ticket.occupied_seat_id is None

        log_entries_after = ticket_log_service.get_entries_for_ticket(ticket.id)
        event_types_after = {entry.event_type for entry in log_entries_after}
        assert 'seat-released' in event_types_after
