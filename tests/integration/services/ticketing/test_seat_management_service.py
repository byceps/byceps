"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

import pytest

from byceps.services.seating import seat_service, seating_area_service

# Import models to ensure the corresponding tables are created so
# `Seat.assignment` is available.
import byceps.services.seating.dbmodels.seat_group  # noqa: F401
from byceps.services.seating.models import SeatID
from byceps.services.ticketing import (
    ticket_bundle_service,
    ticket_creation_service,
    ticket_seat_management_service,
)
from byceps.services.ticketing.errors import (
    SeatChangeDeniedForBundledTicketError,
    TicketCategoryMismatchError,
)
from byceps.services.ticketing.log import ticket_log_service

from tests.helpers import generate_token


@pytest.fixture(scope='module')
def area(party):
    token = generate_token()
    return seating_area_service.create_area(party.id, token, token)


@pytest.fixture()
def seat1(area, category):
    return seat_service.create_seat(area.id, 0, 1, category.id)


@pytest.fixture()
def seat2(area, category):
    return seat_service.create_seat(area.id, 0, 2, category.id)


@pytest.fixture()
def seat_of_another_category(area, another_category):
    return seat_service.create_seat(area.id, 0, 0, another_category.id)


@pytest.fixture()
def ticket(admin_app, category, ticket_owner):
    return ticket_creation_service.create_ticket(category, ticket_owner)


@pytest.fixture()
def ticket_bundle(category, ticket_owner, *, ticket_quantity=1):
    return ticket_bundle_service.create_bundle(
        category, ticket_quantity, ticket_owner
    )


def test_appoint_and_withdraw_seat_manager(
    admin_app, ticket_owner, ticket, ticket_manager
):
    assert ticket.seat_managed_by_id is None

    # appoint seat manager

    appoint_seat_manager_result = (
        ticket_seat_management_service.appoint_seat_manager(
            ticket.id, ticket_manager, ticket_owner
        )
    )
    assert appoint_seat_manager_result.is_ok()
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
            'initiator_id': str(ticket_owner.id),
        },
    )

    # withdraw seat manager

    withdraw_seat_manager_result = (
        ticket_seat_management_service.withdraw_seat_manager(
            ticket.id, ticket_owner
        )
    )
    assert withdraw_seat_manager_result.is_ok()
    assert ticket.seat_managed_by_id is None

    log_entries_after_withdrawal = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_withdrawal) == 2

    withdrawal_log_entry = log_entries_after_withdrawal[1]
    assert_log_entry(
        withdrawal_log_entry,
        'seat-manager-withdrawn',
        {'initiator_id': str(ticket_owner.id)},
    )


def test_occupy_and_release_seat(admin_app, seat1, seat2, ticket_owner, ticket):
    assert ticket.occupied_seat_id is None

    # occupy seat

    occupy_seat_result1 = ticket_seat_management_service.occupy_seat(
        ticket.id, seat1.id, ticket_owner
    )
    assert occupy_seat_result1.is_ok()
    assert ticket.occupied_seat_id == seat1.id

    log_entries_after_occupation = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_occupation) == 1

    occupation_log_entry = log_entries_after_occupation[0]
    assert_log_entry(
        occupation_log_entry,
        'seat-occupied',
        {'seat_id': str(seat1.id), 'initiator_id': str(ticket_owner.id)},
    )

    # switch to another seat

    occupy_seat_result2 = ticket_seat_management_service.occupy_seat(
        ticket.id, seat2.id, ticket_owner
    )
    assert occupy_seat_result2.is_ok()
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
            'initiator_id': str(ticket_owner.id),
        },
    )

    # release seat

    release_seat_result = ticket_seat_management_service.release_seat(
        ticket.id, ticket_owner
    )
    assert release_seat_result.is_ok()
    assert ticket.occupied_seat_id is None

    log_entries_after_release = ticket_log_service.get_entries_for_ticket(
        ticket.id
    )
    assert len(log_entries_after_release) == 3

    release_log_entry = log_entries_after_release[2]
    assert_log_entry(
        release_log_entry,
        'seat-released',
        {'seat_id': str(seat2.id), 'initiator_id': str(ticket_owner.id)},
    )


def test_occupy_seat_with_invalid_id(admin_app, ticket_owner, ticket):
    invalid_seat_id = SeatID(UUID('ffffffff-ffff-ffff-ffff-ffffffffffff'))

    with pytest.raises(ValueError):
        ticket_seat_management_service.occupy_seat(
            ticket.id, invalid_seat_id, ticket_owner
        )


def test_occupy_seat_with_bundled_ticket(
    admin_app, ticket_owner, ticket_bundle, seat1, ticket
):
    bundled_ticket_id = list(ticket_bundle.ticket_ids)[0]

    actual = ticket_seat_management_service.occupy_seat(
        bundled_ticket_id, seat1.id, ticket_owner
    )
    assert isinstance(
        actual.unwrap_err(), SeatChangeDeniedForBundledTicketError
    )


def test_occupy_seat_with_wrong_category(
    admin_app, another_category, seat_of_another_category, ticket_owner, ticket
):
    assert ticket.category_id != another_category.id

    actual = ticket_seat_management_service.occupy_seat(
        ticket.id, seat_of_another_category.id, ticket_owner
    )
    assert isinstance(actual.unwrap_err(), TicketCategoryMismatchError)


# helpers


def assert_log_entry(log_entry, event_type, data):
    assert log_entry.event_type == event_type
    assert log_entry.data == data
