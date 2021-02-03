"""
byceps.services.authentication.session.models.current_user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set

from .....services.user.transfer.models import User
from .....typing import UserID


@dataclass(eq=False, frozen=True)
class CurrentUser:
    """The current user, anonymous or logged in."""

    id: UserID
    screen_name: Optional[str]
    avatar_url: Optional[str]
    is_orga: bool
    is_active: bool
    is_anonymous: bool
    permissions: Set[Enum]

    def has_permission(self, permission: Enum) -> bool:
        return permission in self.permissions

    def has_any_permission(self, *permissions: Set[Enum]) -> bool:
        return any(map(self.has_permission, permissions))

    def to_dto(self) -> User:
        suspended = False  # Current user cannot be suspended.
        deleted = False  # Current user cannot be deleted.

        return User(
            self.id,
            self.screen_name,
            suspended,
            deleted,
            self.avatar_url,
            self.is_orga,
        )

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)
