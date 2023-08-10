"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

from freezegun import freeze_time

from byceps.services.orga import orga_birthday_service
from byceps.services.orga.models import Birthday


@freeze_time('1994-09-30')
def test_sort(make_user):
    born1985 = (make_user(), Birthday(date(1985, 9, 29)))
    born1987 = (make_user(), Birthday(date(1987, 10, 1)))
    born1991 = (make_user(), Birthday(date(1991, 11, 14)))
    born1992 = (make_user(), Birthday(date(1992, 11, 14)))
    born1994 = (make_user(), Birthday(date(1994, 9, 30)))

    users_and_birthdays = [
        born1994,
        born1992,
        born1985,
        born1991,
        born1987,
    ]

    expected = [
        born1994,
        born1987,
        born1991,
        born1992,
        born1985,
    ]

    actual = list(
        orga_birthday_service.sort_users_by_next_birthday(users_and_birthdays)
    )
    assert actual == expected
