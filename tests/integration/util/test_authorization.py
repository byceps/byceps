"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from enum import Enum

from flask import g
import pytest

from byceps.util.authorization import create_permission_enum
from byceps.util.authorization import (
    has_current_user_any_permission,
    has_current_user_permission,
)


ChillPermission = create_permission_enum(
    'chill', ['browse_the_web', 'play_videogames', 'watch_movies']
)


class CurrentUserMock:
    def __init__(self, permissions: set[Enum]) -> None:
        self.permissions = permissions


@pytest.mark.parametrize(
    'permissions_assigned, permission_requested, expected',
    [
        (
            {},
            ChillPermission.browse_the_web,
            False,
        ),
        (
            {ChillPermission.watch_movies},
            ChillPermission.play_videogames,
            False,
        ),
        (
            {ChillPermission.watch_movies},
            ChillPermission.watch_movies,
            True,
        ),
        (
            {
                ChillPermission.browse_the_web,
                ChillPermission.play_videogames,
            },
            ChillPermission.watch_movies,
            False,
        ),
        (
            {
                ChillPermission.browse_the_web,
                ChillPermission.play_videogames,
            },
            ChillPermission.play_videogames,
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
    'permissions_assigned, permissions_requested, expected',
    [
        (
            {},
            {
                ChillPermission.browse_the_web,
            },
            False,
        ),
        (
            {ChillPermission.watch_movies},
            {
                ChillPermission.browse_the_web,
                ChillPermission.play_videogames,
            },
            False,
        ),
        (
            {ChillPermission.watch_movies},
            {
                ChillPermission.play_videogames,
                ChillPermission.watch_movies,
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
