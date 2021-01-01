"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date
from typing import Tuple

from freezegun import freeze_time

from byceps.services.orga import birthday_service
from byceps.services.orga.transfer.models import Birthday
from byceps.services.user.transfer.models import User


@freeze_time('1994-09-30')
def test_sort():
    born1985 = create_user_and_birthday(date(1985,  9, 29))
    born1987 = create_user_and_birthday(date(1987, 10,  1))
    born1991 = create_user_and_birthday(date(1991, 11, 14))
    born1992 = create_user_and_birthday(date(1992, 11, 14))
    born1994 = create_user_and_birthday(date(1994,  9, 30))

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
        birthday_service.sort_users_by_next_birthday(users_and_birthdays)
    )
    assert actual == expected


# helpers


def create_user_and_birthday(date_of_birth: date) -> Tuple[User, Birthday]:
    user = User(
        '55ecd4f2-37ca-4cab-a771-79cf3dabb7cb',
        f'born-{date_of_birth}',
        False,
        False,
        None,
        False,
    )
    birthday = Birthday(date_of_birth)
    return user, birthday
