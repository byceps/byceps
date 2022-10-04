"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pytest import raises

from byceps.services.user import user_service


def test_find_user_by_screen_name_found(admin_app, make_user):
    screen_name = 'ghost'

    user = make_user(screen_name)

    actual = user_service.find_user_by_screen_name(screen_name)

    assert actual.id == user.id


def test_find_user_by_screen_name_not_found(admin_app):
    actual = user_service.find_user_by_screen_name('unknown_dude')

    assert actual is None


def test_get_email_address_found(admin_app, make_user):
    email_address = 'lanparty@lar.ge'

    user = make_user('xpandr', email_address=email_address)

    actual = user_service.get_email_address(user.id)

    assert actual == email_address


def test_get_email_address_not_found(admin_app):
    unknown_user_id = UUID('00000000-0000-0000-0000-000000000001')

    with raises(ValueError):
        user_service.get_email_address(unknown_user_id)
