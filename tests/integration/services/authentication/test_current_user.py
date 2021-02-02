"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from byceps.services.authentication.session import service as session_service
from byceps.util.authorization import create_permission_enum


def test_get_anonymous_current_user():
    current_user = session_service.get_anonymous_current_user()

    assert current_user.id == UUID('00000000-0000-0000-0000-000000000000')
    assert current_user.screen_name is None
    assert current_user.avatar_url is None
    assert not current_user.is_orga
    assert not current_user.is_active
    assert current_user.is_anonymous
    assert len(current_user.permissions) == 0

    dto = current_user.to_dto()
    assert not dto.suspended
    assert not dto.deleted


def test_get_authenticated_current_user(user):
    permission_enum = create_permission_enum('example', ['do_this', 'do_that'])
    permissions = {
        permission_enum.do_this,
        permission_enum.do_that,
    }

    current_user = session_service.get_authenticated_current_user(
        user, permissions
    )

    assert current_user.id == user.id
    assert current_user.screen_name == user.screen_name
    assert current_user.avatar_url is None
    assert not current_user.is_orga
    assert current_user.is_active
    assert not current_user.is_anonymous
    assert current_user.permissions == permissions

    dto = current_user.to_dto()
    assert not dto.suspended
    assert not dto.deleted
