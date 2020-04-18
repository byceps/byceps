"""

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.seating import (
    area_service as seating_area_service,
    seat_service,
)
from byceps.services.ticketing import (
    event_service,
    ticket_creation_service,
    ticket_revocation_service,
    ticket_seat_management_service,
    ticket_service,
)

# Import models to ensure the corresponding tables are created so
# `Seat.assignment` is available.
import byceps.services.seating.models.seat_group


@pytest.fixture(scope='module')
def area(party):
    return seating_area_service.create_area(party.id, 'main', 'Main Hall')


@pytest.fixture
def ticket(category, ticket_owner):
    return ticket_creation_service.create_ticket(category.id, ticket_owner.id)


@pytest.fixture
def tickets(category, ticket_owner):
    quantity = 3
    return ticket_creation_service.create_tickets(
        category.id, ticket_owner.id, quantity
    )


def test_revoke_ticket(app, ticket, ticketing_admin):
    ticket_before = ticket
    assert not ticket_before.revoked

    events_before = event_service.get_events_for_ticket(ticket_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    ticket_id = ticket_before.id

    ticket_revocation_service.revoke_ticket(ticket_id, ticketing_admin.id)

    # -------------------------------- #

    ticket_after = ticket_service.find_ticket(ticket_id)
    assert ticket_after.revoked

    events_after = event_service.get_events_for_ticket(ticket_after.id)
    assert len(events_after) == 1

    ticket_revoked_event = events_after[0]
    assert ticket_revoked_event.event_type == 'ticket-revoked'
    assert ticket_revoked_event.data == {
        'initiator_id': str(ticketing_admin.id)
    }


def test_revoke_tickets(app, tickets, ticketing_admin):
    tickets_before = tickets

    for ticket_before in tickets_before:
        assert not ticket_before.revoked

        events_before = event_service.get_events_for_ticket(ticket_before.id)
        assert len(events_before) == 0

    # -------------------------------- #

    ticket_ids = {ticket.id for ticket in tickets_before}

    ticket_revocation_service.revoke_tickets(ticket_ids, ticketing_admin.id)

    # -------------------------------- #

    tickets_after = ticket_service.find_tickets(ticket_ids)
    for ticket_after in tickets_after:
        assert ticket_after.revoked

        events_after = event_service.get_events_for_ticket(ticket_after.id)
        assert len(events_after) == 1

        ticket_revoked_event = events_after[0]
        assert ticket_revoked_event.event_type == 'ticket-revoked'
        assert ticket_revoked_event.data == {
            'initiator_id': str(ticketing_admin.id)
        }


def test_revoke_ticket_with_seat(app, area, ticket, ticketing_admin):
    seat = seat_service.create_seat(area, 0, 0, ticket.category_id)

    ticket_seat_management_service.occupy_seat(
        ticket.id, seat.id, ticket.owned_by_id
    )

    assert ticket.occupied_seat_id == seat.id

    events_before = event_service.get_events_for_ticket(ticket.id)
    event_types_before = {event.event_type for event in events_before}
    assert 'seat-released' not in event_types_before

    # -------------------------------- #

    ticket_revocation_service.revoke_ticket(ticket.id, ticketing_admin.id)

    # -------------------------------- #

    assert ticket.occupied_seat_id is None

    events_after = event_service.get_events_for_ticket(ticket.id)
    event_types_after = {event.event_type for event in events_after}
    assert 'seat-released' in event_types_after


def test_revoke_tickets_with_seats(app, area, tickets, ticketing_admin):
    ticket_ids = {ticket.id for ticket in tickets}

    for ticket in tickets:
        seat = seat_service.create_seat(area, 0, 0, ticket.category_id)

        ticket_seat_management_service.occupy_seat(
            ticket.id, seat.id, ticket.owned_by_id
        )

        assert ticket.occupied_seat_id == seat.id

    # -------------------------------- #

    ticket_revocation_service.revoke_tickets(ticket_ids, ticketing_admin.id)

    # -------------------------------- #

    for ticket in tickets:
        assert ticket.occupied_seat_id is None

        events_after = event_service.get_events_for_ticket(ticket.id)
        event_types_after = {event.event_type for event in events_after}
        assert 'seat-released' in event_types_after
