"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from babel import Locale

from byceps.services.authn.session.models import CurrentUser


def test_create_anonymous_current_user():
    locale = Locale('en')

    current_user = CurrentUser.create_anonymous(locale)

    assert current_user.id == UUID('00000000-0000-0000-0000-000000000000')
    assert current_user.screen_name is None
    assert not current_user.suspended
    assert not current_user.deleted
    assert current_user.avatar_url == '/static/user_avatar_fallback.svg'
    assert not current_user.authenticated
    assert len(current_user.permissions) == 0
    assert current_user.locale == locale


def test_create_authenticated_current_user(user):
    locale = Locale('de')
    permissions = frozenset(
        [
            'example.do_this',
            'example.do_that',
        ]
    )

    current_user = CurrentUser.create_authenticated(user, locale, permissions)

    assert current_user.id == user.id
    assert current_user.screen_name == user.screen_name
    assert not current_user.suspended
    assert not current_user.deleted
    assert current_user.avatar_url == '/static/user_avatar_fallback.svg'
    assert current_user.authenticated
    assert current_user.permissions == permissions
    assert current_user.locale == locale
