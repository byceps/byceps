"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID

from pytest import raises

from byceps.services.user import service as user_service

from tests.helpers import create_user


def test_find_user_by_screen_name_found(admin_app_with_db):
    screen_name = 'ghost'

    user = create_user(screen_name)

    actual = user_service.find_user_by_screen_name(screen_name)

    assert actual.id == user.id


def test_find_user_by_screen_name_not_found(admin_app_with_db):
    actual = user_service.find_user_by_screen_name('unknown_dude')

    assert actual is None


def test_get_anonymous_user(admin_app_with_db):
    user = user_service.get_anonymous_user()

    assert user.id == UUID('00000000-0000-0000-0000-000000000000')

    assert not user.deleted

    assert user.avatar is None
    assert user.avatar_url is None

    assert not user.is_orga


def test_get_email_address_found(admin_app_with_db):
    email_address = 'lanparty@lar.ge'

    user = create_user('xpandr', email_address=email_address)

    actual = user_service.get_email_address(user.id)

    assert actual == email_address


def test_get_email_address_not_found(admin_app_with_db):
    unknown_user_id = UUID('00000000-0000-0000-0000-000000000001')

    with raises(ValueError):
        user_service.get_email_address(unknown_user_id)
