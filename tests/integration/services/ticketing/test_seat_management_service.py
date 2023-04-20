"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.seating import seat_service, seating_area_service

# Import models to ensure the corresponding tables are created so
# `Seat.assignment` is available.
import byceps.services.seating.dbmodels.seat_group  # noqa: F401

from byceps.services.ticketing import (
    ticket_bundle_service,
    ticket_creation_service,
    ticket_log_service,
    ticket_seat_management_service,
    ticket_service,
)
from byceps.services.ticketing.exceptions import (
    SeatChangeDeniedForBundledTicket,
    TicketCategoryMismatch,
)


@pytest.fixture(scope='module')
def area(party):
    area = seating_area_service.create_area(party.id, 'main', 'Main Hall')
    yield area
    seating_area_service.delete_area(area.id)


@pytest.fixture
def seat1(area, category):
    seat = seat_service.create_seat(area.id, 0, 1, category.id)
    yield seat
    seat_service.delete_seat(seat.id)


@pytest.fixture
def seat2(area, category):
    seat = seat_service.create_seat(area.id, 0, 2, category.id)
    yield seat
    seat_service.delete_seat(seat.id)


@pytest.fixture
def seat_of_another_category(area, another_category):
    seat = seat_service.create_seat(area.id, 0, 0, another_category.id)
    yield seat
    seat_service.delete_seat(seat.id)


@pytest.fixture
def ticket(admin_app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )
    yield ticket
    ticket_service.delete_ticket(ticket.id)


@pytest.fixture
def ticket_bundle(category, ticket_owner):
    ticket_quantity = 1
    bundle = ticket_bundle_service.create_bundle(
        category.party_id, category.id, ticket_quantity, ticket_owner.id
    )
    yield bundle
    ticket_bundle_service.delete_bundle(bundle.id)


def test_appoint_and_withdraw_seat_manager(admin_app, ticket, ticket_manager):
    assert ticket.seat_managed_by_id is None

    # appoint seat manager

    ticket_seat_management_service.appoint_seat_manager(
        ticket.id, ticket_manager.id, ticket.owned_by_id
    )
    assert ticket.seat_managed_by_id == ticket_manager.id

    log_entries_after_appointment = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_appointment) == 1

    appointment_log_entry = log_entries_after_appointment[0]
    assert_log_entry(
        appointment_log_entry,
        'seat-manager-appointed',
        {
            'appointed_seat_manager_id': str(ticket_manager.id),
            'initiator_id': str(ticket.owned_by_id),
        },
    )

    # withdraw seat manager

    ticket_seat_management_service.withdraw_seat_manager(
        ticket.id, ticket.owned_by_id
    )
    assert ticket.seat_managed_by_id is None

    log_entries_after_withdrawal = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_withdrawal) == 2

    withdrawal_log_entry = log_entries_after_withdrawal[1]
    assert_log_entry(
        withdrawal_log_entry,
        'seat-manager-withdrawn',
        {'initiator_id': str(ticket.owned_by_id)},
    )


def test_occupy_and_release_seat(admin_app, seat1, seat2, ticket):
    assert ticket.occupied_seat_id is None

    # occupy seat

    ticket_seat_management_service.occupy_seat(
        ticket.id, seat1.id, ticket.owned_by_id
    )
    assert ticket.occupied_seat_id == seat1.id

    log_entries_after_occupation = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_occupation) == 1

    occupation_log_entry = log_entries_after_occupation[0]
    assert_log_entry(
        occupation_log_entry,
        'seat-occupied',
        {'seat_id': str(seat1.id), 'initiator_id': str(ticket.owned_by_id)},
    )

    # switch to another seat

    ticket_seat_management_service.occupy_seat(
        ticket.id, seat2.id, ticket.owned_by_id
    )
    assert ticket.occupied_seat_id == seat2.id

    log_entries_after_switch = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_switch) == 2

    switch_log_entry = log_entries_after_switch[1]
    assert_log_entry(
        switch_log_entry,
        'seat-occupied',
        {
            'previous_seat_id': str(seat1.id),
            'seat_id': str(seat2.id),
            'initiator_id': str(ticket.owned_by_id),
        },
    )

    # release seat

    ticket_seat_management_service.release_seat(ticket.id, ticket.owned_by_id)
    assert ticket.occupied_seat_id is None

    log_entries_after_release = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_release) == 3

    release_log_entry = log_entries_after_release[2]
    assert_log_entry(
        release_log_entry,
        'seat-released',
        {'seat_id': str(seat2.id), 'initiator_id': str(ticket.owned_by_id)},
    )


def test_occupy_seat_with_invalid_id(admin_app, ticket):
    invalid_seat_id = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

    with pytest.raises(ValueError):
        ticket_seat_management_service.occupy_seat(
            ticket.id, invalid_seat_id, ticket.owned_by_id
        )


def test_occupy_seat_with_bundled_ticket(
    admin_app, ticket_bundle, seat1, ticket
):
    bundled_ticket = ticket_bundle.tickets[0]

    with pytest.raises(SeatChangeDeniedForBundledTicket):
        ticket_seat_management_service.occupy_seat(
            bundled_ticket.id, seat1.id, ticket.owned_by_id
        )


def test_occupy_seat_with_wrong_category(
    admin_app, another_category, seat_of_another_category, ticket
):
    assert ticket.category_id != another_category.id

    with pytest.raises(TicketCategoryMismatch):
        ticket_seat_management_service.occupy_seat(
            ticket.id, seat_of_another_category.id, ticket.owned_by_id
        )


# helpers


def assert_log_entry(log_entry, event_type, data):
    assert log_entry.event_type == event_type
    assert log_entry.data == data
