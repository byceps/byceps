"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2020, 3, 21, 14, 59, 59), False),
        (datetime(2020, 3, 21, 15, 0, 0), False),
        (datetime(2020, 3, 21, 15, 0, 1), True),
    ],
)
def test_is_over(make_party, now, expected):
    ends_at = datetime(2020, 3, 21, 15, 0, 0)
    party = make_party(ends_at=ends_at)

    with freeze_time(now):
        assert party.is_over == expected
