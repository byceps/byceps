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
)

from tests.helpers import generate_uuid


@pytest.mark.parametrize(
    ('ticket_quantity', 'now', 'expected'),
    [
        (11, datetime(2025, 6, 16, 18, 0, 0), False),  # too early
        (11, datetime(2025, 6, 17, 18, 0, 0), True),
        (10, datetime(2025, 6, 17, 18, 0, 0), True),
        (10, datetime(2025, 6, 17, 18, 0, 0), True),
        (10, datetime(2025, 6, 17, 17, 59, 59), False),  # too early
        (9, datetime(2025, 6, 17, 18, 0, 0), False),  # too few tickets
        (6, datetime(2025, 6, 18, 18, 0, 0), True),
        (5, datetime(2025, 6, 18, 18, 0, 0), True),
        (5, datetime(2025, 6, 18, 18, 0, 0), True),
        (5, datetime(2025, 6, 18, 17, 59, 59), False),  # too early
        (4, datetime(2025, 6, 18, 18, 0, 0), False),  # too few tickets
        (2, datetime(2025, 6, 19, 18, 0, 0), True),
        (1, datetime(2025, 6, 19, 18, 0, 0), True),
        (1, datetime(2025, 6, 19, 18, 0, 0), True),
        (1, datetime(2025, 6, 19, 17, 59, 59), False),  # too early
        (0, datetime(2025, 6, 19, 18, 0, 0), False),  # too few tickets
        (1, datetime(2025, 6, 20, 18, 0, 0), True),
        (0, datetime(2025, 6, 20, 18, 0, 0), False),  # too few tickets
    ],
)
def test_are_preconditions_met(preconditions, ticket_quantity, now, expected):
    actual = are_preconditions_met(preconditions, ticket_quantity, now)
    assert actual == expected


@pytest.fixture(scope='module')
def preconditions() -> set[SeatReservationPrecondition]:
    party_id = PartyID('party-2025')

    return {
        SeatReservationPrecondition(
            id=generate_uuid(),
            party_id=party_id,
            minimum_ticket_quantity=10,
            at_earliest=datetime(2025, 6, 17, 18, 0, 0),
        ),
        SeatReservationPrecondition(
            id=generate_uuid(),
            party_id=party_id,
            minimum_ticket_quantity=5,
            at_earliest=datetime(2025, 6, 18, 18, 0, 0),
        ),
        SeatReservationPrecondition(
            id=generate_uuid(),
            party_id=party_id,
            minimum_ticket_quantity=1,
            at_earliest=datetime(2025, 6, 19, 18, 0, 0),
        ),
    }


def test_reservation_without_preconditions_is_denied():
    preconditions = {}
    ticket_quantity = 99
    now = datetime(2025, 6, 20, 18, 0, 0)

    assert not are_preconditions_met(preconditions, ticket_quantity, now)
