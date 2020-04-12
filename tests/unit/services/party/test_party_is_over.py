"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime, timedelta

from freezegun import freeze_time
import pytest

from byceps.services.party.transfer.models import Party


@pytest.mark.parametrize('now, expected', [
    (datetime(2020,  3,  21, 14, 59, 59), False),
    (datetime(2020,  3,  21, 15,  0,  0), False),
    (datetime(2020,  3,  21, 15,  0,  1), True),
])
def test_is_over(now, expected):
    ends_at = datetime(2020, 3, 21, 15, 0 ,0)
    party = create_party(ends_at)

    with freeze_time(now):
        assert party.is_over == expected


# helpers


def create_party(ends_at: datetime) -> Party:
    starts_at = ends_at - timedelta(days=2)
    return Party(
        'anylan-20',
        'anylan',
        'AnyLAN #20',
        starts_at,
        ends_at,
        0,
        'any-shop-id',
        False,
        False,
        False,
    )
