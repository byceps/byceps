"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from byceps.services.authentication.session import service as session_service
from byceps.util.authorization import create_permission_enum


def test_get_anonymous_current_user():
    locale = 'en'

    current_user = session_service.get_anonymous_current_user(locale=locale)

    assert current_user.id == UUID('00000000-0000-0000-0000-000000000000')
    assert current_user.screen_name is None
    assert not current_user.suspended
    assert not current_user.deleted
    assert current_user.avatar_url is None
    assert not current_user.is_orga
    assert not current_user.authenticated
    assert len(current_user.permissions) == 0
    assert current_user.locale == 'en'


def test_get_authenticated_current_user(user):
    permission_enum = create_permission_enum('example', ['do_this', 'do_that'])
    permissions = frozenset([
        permission_enum.do_this,
        permission_enum.do_that,
    ])
    locale = 'de'

    current_user = session_service.get_authenticated_current_user(
        user, permissions=permissions, locale=locale
    )

    assert current_user.id == user.id
    assert current_user.screen_name == user.screen_name
    assert not current_user.suspended
    assert not current_user.deleted
    assert current_user.avatar_url is None
    assert not current_user.is_orga
    assert current_user.authenticated
    assert current_user.permissions == permissions
    assert current_user.locale == 'de'
