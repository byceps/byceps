"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import date

from freezegun import freeze_time

from byceps.database import generate_uuid
from byceps.services.orga import birthday_service
from byceps.services.orga.transfer.models import Birthday
from byceps.services.user.transfer.models import User
from byceps.typing import UserID


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


def create_user_and_birthday(date_of_birth: date) -> tuple[User, Birthday]:
    user = User(
        id=UserID(generate_uuid()),
        screen_name=f'born-{date_of_birth}',
        suspended=False,
        deleted=False,
        locale=None,
        avatar_url=None,
    )
    birthday = Birthday(date_of_birth)
    return user, birthday
