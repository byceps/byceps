"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.party.models import PartyID
from byceps.services.seating.models import SeatReservationPrecondition
from byceps.services.seating.seat_reservation_domain_service import (
    are_preconditions_met,
    create_precondition,
)


@pytest.mark.parametrize(
    ('now', 'ticket_quantity', 'expected'),
    [
        (datetime(2025, 6, 16, 18, 0, 0), 11, False),  # too early
        (datetime(2025, 6, 17, 18, 0, 0), 11, True),
        (datetime(2025, 6, 17, 18, 0, 0), 10, True),
        (datetime(2025, 6, 17, 18, 0, 0), 10, True),
        (datetime(2025, 6, 17, 17, 59, 59), 10, False),  # too early
        (datetime(2025, 6, 17, 18, 0, 0), 9, False),  # too few tickets
        (datetime(2025, 6, 18, 18, 0, 0), 6, True),
        (datetime(2025, 6, 18, 18, 0, 0), 5, True),
        (datetime(2025, 6, 18, 18, 0, 0), 5, True),
        (datetime(2025, 6, 18, 17, 59, 59), 5, False),  # too early
        (datetime(2025, 6, 18, 18, 0, 0), 4, False),  # too few tickets
        (datetime(2025, 6, 19, 18, 0, 0), 2, True),
        (datetime(2025, 6, 19, 18, 0, 0), 1, True),
        (datetime(2025, 6, 19, 18, 0, 0), 1, True),
        (datetime(2025, 6, 19, 17, 59, 59), 1, False),  # too early
        (datetime(2025, 6, 19, 18, 0, 0), 0, False),  # too few tickets
        (datetime(2025, 6, 20, 18, 0, 0), 1, True),
        (datetime(2025, 6, 20, 18, 0, 0), 0, False),  # too few tickets
    ],
)
def test_are_preconditions_met(preconditions, now, ticket_quantity, expected):
    actual = are_preconditions_met(preconditions, now, ticket_quantity)
    assert actual == expected


@pytest.fixture(scope='module')
def preconditions() -> set[SeatReservationPrecondition]:
    party_id = PartyID('party-2025')

    return {
        create_precondition(party_id, datetime(2025, 6, 17, 18, 0, 0), 10),
        create_precondition(party_id, datetime(2025, 6, 18, 18, 0, 0), 5),
        create_precondition(party_id, datetime(2025, 6, 19, 18, 0, 0), 1),
    }


def test_reservation_without_preconditions_is_denied():
    preconditions = {}
    now = datetime(2025, 6, 20, 18, 0, 0)
    ticket_quantity = 99

    assert not are_preconditions_met(preconditions, now, ticket_quantity)
