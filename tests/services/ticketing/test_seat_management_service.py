"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest
from pytest import raises

from byceps.services.seating import area_service, seat_service
from byceps.services.ticketing import (
    event_service,
    ticket_bundle_service,
    ticket_creation_service,
    ticket_seat_management_service,
)
from byceps.services.ticketing.exceptions import (
    SeatChangeDeniedForBundledTicket,
    TicketCategoryMismatch,
)

# Import models to ensure the corresponding tables are created so
# `Seat.assignment` is available.
import byceps.services.seating.models.seat_group


@pytest.fixture(scope='module')
def area(party):
    return area_service.create_area(party.id, 'main', 'Main Hall')


@pytest.fixture
def ticket(app, category, ticket_owner):
    return ticket_creation_service.create_ticket(category.id, ticket_owner.id)


def test_appoint_and_withdraw_seat_manager(
    app, category, ticket, ticket_owner, ticket_manager
):
    assert ticket.seat_managed_by_id is None

    # appoint seat manager

    ticket_seat_management_service.appoint_seat_manager(
        ticket.id, ticket_manager.id, ticket_owner.id
    )
    assert ticket.seat_managed_by_id == ticket_manager.id

    events_after_appointment = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_appointment) == 1

    appointment_event = events_after_appointment[0]
    assert_event(
        appointment_event,
        'seat-manager-appointed',
        {
            'appointed_seat_manager_id': str(ticket_manager.id),
            'initiator_id': str(ticket_owner.id),
        },
    )

    # withdraw seat manager

    ticket_seat_management_service.withdraw_seat_manager(
        ticket.id, ticket_owner.id
    )
    assert ticket.seat_managed_by_id is None

    events_after_withdrawal = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_withdrawal) == 2

    withdrawal_event = events_after_withdrawal[1]
    assert_event(
        withdrawal_event,
        'seat-manager-withdrawn',
        {'initiator_id': str(ticket_owner.id)},
    )


def test_occupy_and_release_seat(app, category, area, ticket, ticket_owner):
    seat1 = seat_service.create_seat(area, 0, 1, category.id)
    seat2 = seat_service.create_seat(area, 0, 2, category.id)

    assert ticket.occupied_seat_id is None

    # occupy seat

    ticket_seat_management_service.occupy_seat(
        ticket.id, seat1.id, ticket_owner.id
    )
    assert ticket.occupied_seat_id == seat1.id

    events_after_occupation = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_occupation) == 1

    occupation_event = events_after_occupation[0]
    assert_event(
        occupation_event,
        'seat-occupied',
        {'seat_id': str(seat1.id), 'initiator_id': str(ticket_owner.id)},
    )

    # switch to another seat

    ticket_seat_management_service.occupy_seat(
        ticket.id, seat2.id, ticket_owner.id
    )
    assert ticket.occupied_seat_id == seat2.id

    events_after_switch = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_switch) == 2

    switch_event = events_after_switch[1]
    assert_event(
        switch_event,
        'seat-occupied',
        {
            'previous_seat_id': str(seat1.id),
            'seat_id': str(seat2.id),
            'initiator_id': str(ticket_owner.id),
        },
    )

    # release seat

    ticket_seat_management_service.release_seat(ticket.id, ticket_owner.id)
    assert ticket.occupied_seat_id is None

    events_after_release = event_service.get_events_for_ticket(ticket.id)
    assert len(events_after_release) == 3

    release_event = events_after_release[2]
    assert_event(
        release_event,
        'seat-released',
        {'seat_id': str(seat2.id), 'initiator_id': str(ticket_owner.id)},
    )


def test_occupy_seat_with_invalid_id(app, category, ticket, ticket_owner):
    invalid_seat_id = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

    with raises(ValueError):
        ticket_seat_management_service.occupy_seat(
            ticket.id, invalid_seat_id, ticket_owner.id
        )


def test_occupy_seat_with_bundled_ticket(
    app, category, area, ticket, ticket_owner
):
    ticket_quantity = 1
    ticket_bundle = ticket_bundle_service.create_bundle(
        category.id, ticket_quantity, ticket_owner.id
    )

    bundled_ticket = ticket_bundle.tickets[0]

    seat = seat_service.create_seat(area, 0, 0, category.id)

    with raises(SeatChangeDeniedForBundledTicket):
        ticket_seat_management_service.occupy_seat(
            bundled_ticket.id, seat.id, ticket_owner.id
        )


def test_occupy_seat_with_wrong_category(
    app, party, category, another_category, area, ticket, ticket_owner
):
    seat = seat_service.create_seat(area, 0, 0, another_category.id)

    assert ticket.category_id != another_category.id

    with raises(TicketCategoryMismatch):
        ticket_seat_management_service.occupy_seat(
            ticket.id, seat.id, ticket_owner.id
        )


# helpers


def assert_event(event, event_type, data):
    assert event.event_type == event_type
    assert event.data == data
