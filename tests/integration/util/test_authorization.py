"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g
from flask_babel import lazy_gettext
import pytest

from byceps.util.authorization import (
    has_current_user_any_permission,
    has_current_user_permission,
    register_permissions,
)


register_permissions(
    'chill',
    [
        ('browse_the_web', lazy_gettext('Browse the web')),
        ('play_video_games', lazy_gettext('Play video games')),
        ('watch_movies', lazy_gettext('Watch movies')),
    ],
)


class CurrentUserMock:
    def __init__(self, permissions: set[str]) -> None:
        self.permissions = permissions


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
def test_has_current_user_permission(
    site_app, permissions_assigned, permission_requested, expected
):
    g.user = CurrentUserMock(permissions_assigned)
    assert has_current_user_permission(permission_requested) == expected


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
def test_has_current_user_any_permission(
    site_app, permissions_assigned, permissions_requested, expected
):
    g.user = CurrentUserMock(permissions_assigned)
    assert has_current_user_any_permission(*permissions_requested) == expected
