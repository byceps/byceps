"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

import pytest

from byceps.services.authn.session.models import CurrentUser
from byceps.services.user.models import UserID


@pytest.mark.parametrize(
    ('permissions_assigned', 'permission_requested', 'expected'),
    [
        (
            {},
            'chill.browse_the_web',
            False,
        ),
        (
            {'chill.watch_movies'},
            'chill.play_video_games',
            False,
        ),
        (
            {'chill.watch_movies'},
            'chill.watch_movies',
            True,
        ),
        (
            {
                'chill.browse_the_web',
                'chill.play_video_games',
            },
            'chill.watch_movies',
            False,
        ),
        (
            {
                'chill.browse_the_web',
                'chill.play_video_games',
            },
            'chill.play_video_games',
            True,
        ),
    ],
)
def test_current_user_has_permission(
    permissions_assigned, permission_requested, expected
):
    current_user = build_current_user(permissions_assigned)
    assert current_user.has_permission(permission_requested) == expected


@pytest.mark.parametrize(
    ('permissions_assigned', 'permissions_requested', 'expected'),
    [
        (
            {},
            {
                'chill.browse_the_web',
            },
            False,
        ),
        (
            {'chill.watch_movies'},
            {
                'chill.browse_the_web',
                'chill.play_video_games',
            },
            False,
        ),
        (
            {'chill.watch_movies'},
            {
                'chill.play_video_games',
                'chill.watch_movies',
            },
            True,
        ),
    ],
)
def test_current_user_has_any_permission(
    permissions_assigned, permissions_requested, expected
):
    current_user = build_current_user(permissions_assigned)
    assert current_user.has_any_permission(*permissions_requested) == expected


def build_current_user(permissions: set[str]) -> CurrentUser:
    return CurrentUser(
        id=UserID(UUID('d14b0dd0-886f-42a1-990a-c2435ae60123')),
        screen_name='SomeUser',
        initialized=True,
        suspended=False,
        deleted=False,
        avatar_url='/static/user_avatar_fallback.svg',
        locale=None,
        authenticated=False,
        permissions=frozenset(permissions),
    )
