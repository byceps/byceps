"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from flask_babel import lazy_gettext

from byceps.services.authentication.session import authn_session_service
from byceps.util.authorization import register_permissions


def test_get_anonymous_current_user():
    locale = 'en'

    current_user = authn_session_service.get_anonymous_current_user(locale)

    assert current_user.id == UUID('00000000-0000-0000-0000-000000000000')
    assert current_user.screen_name is None
    assert not current_user.suspended
    assert not current_user.deleted
    assert current_user.avatar_url is None
    assert not current_user.authenticated
    assert len(current_user.permissions) == 0
    assert current_user.locale == 'en'


def test_get_authenticated_current_user(user):
    register_permissions(
        'example',
        [
            ('do_this', lazy_gettext('Do this')),
            ('do_that', lazy_gettext('Do that')),
        ],
    )
    permissions = frozenset(
        [
            'example.do_this',
            'example.do_that',
        ]
    )
    locale = 'de'

    current_user = authn_session_service.get_authenticated_current_user(
        user, locale, permissions
    )

    assert current_user.id == user.id
    assert current_user.screen_name == user.screen_name
    assert not current_user.suspended
    assert not current_user.deleted
    assert current_user.avatar_url is None
    assert current_user.authenticated
    assert current_user.permissions == permissions
    assert current_user.locale == 'de'
