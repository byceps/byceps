"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import generate_uuid
from byceps.services.user.service import get_sort_key_for_screen_name
from byceps.services.user.transfer.models import User
from byceps.typing import UserID


def test_get_sort_key_for_screen_name():
    user1 = create_user('AnyName')
    user2 = create_user(None)  # no screen name
    user3 = create_user('SomeName')
    user4 = create_user('UpperCaseName')
    user5 = create_user('lowerCaseName')

    users = {user1, user2, user3, user4, user5}

    actual = sorted(users, key=get_sort_key_for_screen_name)

    assert actual == [user1, user5, user3, user4, user2]


def create_user(screen_name: str) -> User:
    return User(
        id=UserID(generate_uuid()),
        screen_name=screen_name,
        suspended=False,
        deleted=False,
        locale=None,
        avatar_url=None,
    )
