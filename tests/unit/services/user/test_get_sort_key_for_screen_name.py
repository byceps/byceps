"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user.user_service import get_sort_key_for_screen_name


def test_get_sort_key_for_screen_name(make_user):
    user1 = make_user(screen_name='AnyName')
    user2 = make_user(screen_name=None)  # no screen name
    user3 = make_user(screen_name='SomeName')
    user4 = make_user(screen_name='UpperCaseName')
    user5 = make_user(screen_name='lowerCaseName')

    users = {user1, user2, user3, user4, user5}

    actual = sorted(users, key=get_sort_key_for_screen_name)

    assert actual == [user1, user5, user3, user4, user2]
