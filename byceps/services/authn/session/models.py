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
class CurrentUser(User):
    """The current user, anonymous or logged in."""

    locale: Locale | None
    authenticated: bool
    permissions: frozenset[str]

    @classmethod
    def create_anonymous(cls, locale: Locale | None) -> Self:
        """Return an anonymous current user object."""
        return cls(
            id=_ANONYMOUS_USER_ID,
            screen_name=None,
            initialized=True,
            suspended=False,
            deleted=False,
            avatar_url=USER_FALLBACK_AVATAR_URL_PATH,
            locale=locale,
            authenticated=False,
            permissions=frozenset(),
        )

    @classmethod
    def create_authenticated(
        cls, user: User, locale: Locale | None, permissions: frozenset[str]
    ) -> Self:
        """Return an authenticated current user object."""
        return cls(
            id=user.id,
            screen_name=user.screen_name,
            initialized=True,  # Current user has to be initialized.
            suspended=False,  # Current user cannot be suspended.
            deleted=False,  # Current user cannot be deleted.
            avatar_url=user.avatar_url,
            locale=locale,
            authenticated=True,
            permissions=permissions,
        )

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)

    def has_permission(self, permission: str) -> bool:
        """Return `True` if the current user has this permission."""
        return permission in self.permissions

    def has_any_permission(self, *permissions: str) -> bool:
        """Return `True` if the current user has any of these permissions."""
        return any(map(self.has_permission, permissions))
