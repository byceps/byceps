"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.seating import seat_service
from byceps.services.seating.transfer.models import SeatUtilization


def test_aggregate_seat_utilizations():
    sus = [
        SeatUtilization(occupied=23, total=60),
        SeatUtilization(occupied=0, total=50),
        SeatUtilization(occupied=42, total=80),
    ]

    expected = SeatUtilization(occupied=65, total=190)

    assert seat_service.aggregate_seat_utilizations(sus) == expected
