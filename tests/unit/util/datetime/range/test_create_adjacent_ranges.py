"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.util.datetime.range import create_adjacent_ranges, DateTimeRange


def test_create_adjacent_ranges():
    dt1 = datetime(2014,  8, 15, 12,  0,  0)
    dt2 = datetime(2014,  8, 15, 19, 30,  0)
    dt3 = datetime(2014,  8, 16,  7, 15,  0)
    dt4 = datetime(2014,  8, 18, 22, 45,  0)

    dts = [dt1, dt2, dt3, dt4]

    expected = [
        DateTimeRange(dt1, dt2),
        DateTimeRange(dt2, dt3),
        DateTimeRange(dt3, dt4),
    ]

    actual = create_adjacent_ranges(dts)

    assert list(actual) == expected
