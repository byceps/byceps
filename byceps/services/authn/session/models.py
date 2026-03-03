"""
byceps.services.authn.session.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Self
from uuid import UUID

from babel import Locale

from byceps.services.user.models import (
    User,
    UserID,
    USER_FALLBACK_AVATAR_URL_PATH,
)


_ANONYMOUS_USER_ID = UserID(UUID('00000000-0000-0000-0000-000000000000'))


@dataclass(eq=False, frozen=True, kw_only=True)
class CurrentUser:
    """The current user, anonymous or logged in."""

    _user: User
    locale: Locale | None
    authenticated: bool
    permissions: frozenset[str]

    @classmethod
    def create_anonymous(cls, locale: Locale | None) -> Self:
        """Return an anonymous current user object."""
        user = User(
            id=_ANONYMOUS_USER_ID,
            screen_name=None,
            initialized=True,
            suspended=False,
            deleted=False,
            avatar_url=USER_FALLBACK_AVATAR_URL_PATH,
        )

        return cls(
            _user=user,
            locale=locale,
            authenticated=False,
            permissions=frozenset(),
        )

    @classmethod
    def create_authenticated(
        cls, user: User, locale: Locale | None, permissions: frozenset[str]
    ) -> Self:
        """Return an authenticated current user object."""
        if not user.initialized:
            raise ValueError('User has to be initialized')

        if user.suspended:
            raise ValueError('User must not be suspended')

        if user.deleted:
            raise ValueError('User must not be deleted')

        user = User(
            id=user.id,
            screen_name=user.screen_name,
            initialized=True,
            suspended=False,
            deleted=False,
            avatar_url=user.avatar_url,
        )

        return cls(
            _user=user,
            locale=locale,
            authenticated=True,
            permissions=permissions,
        )

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)

    @property
    def id(self) -> UserID:
        return self._user.id

    @property
    def screen_name(self) -> str | None:
        return self._user.screen_name

    @property
    def initialized(self) -> bool:
        return self._user.initialized

    @property
    def suspended(self) -> bool:
        return self._user.suspended

    @property
    def deleted(self) -> bool:
        return self._user.deleted

    @property
    def avatar_url(self) -> str:
        return self._user.avatar_url

    def has_permission(self, permission: str) -> bool:
        """Return `True` if the current user has this permission."""
        return permission in self.permissions

    def has_any_permission(self, *permissions: str) -> bool:
        """Return `True` if the current user has any of these permissions."""
        return any(map(self.has_permission, permissions))

    def as_user(self) -> User:
        return self._user
