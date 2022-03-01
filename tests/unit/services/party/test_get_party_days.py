"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime

import pytest

from byceps.services.party import service
from byceps.services.party.transfer.models import Party
from byceps.typing import BrandID, PartyID


@pytest.mark.parametrize(
    'starts_at, ends_at, expected',
    [
        (
            datetime(2020, 8, 22,  9, 30, 0),
            datetime(2020, 8, 22, 23, 30, 0),
            [
                date(2020, 8, 22),
            ]
        ),
        (
            datetime(2020, 3, 16, 14, 0, 0),
            datetime(2020, 3, 18, 11, 0, 0),
            [
                date(2020, 3, 16),
                date(2020, 3, 17),
                date(2020, 3, 18),
            ]
        ),
        (
            datetime(2020, 12, 10, 17, 0, 0),
            datetime(2020, 12, 13, 14, 0, 0),
            [
                date(2020, 12, 10),
                date(2020, 12, 11),
                date(2020, 12, 12),
                date(2020, 12, 13),
            ],
        ),
    ],
)
def test_get_party_days(starts_at, ends_at, expected):
    party = create_party(starts_at, ends_at)
    assert service.get_party_days(party) == expected


# helpers


def create_party(starts_at: datetime, ends_at: datetime) -> Party:
    return Party(
        PartyID('anylan-20'),
        BrandID('anylan'),
        'AnyLAN #20',
        starts_at,
        ends_at,
        0,
        False,
        False,
        False,
        False,
    )
