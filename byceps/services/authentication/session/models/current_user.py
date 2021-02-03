"""
byceps.services.authentication.session.models.current_user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set

from .....services.user.transfer.models import User


@dataclass(eq=False, frozen=True)
class CurrentUser(User):
    """The current user, anonymous or logged in."""

    is_active: bool
    is_anonymous: bool
    permissions: Set[Enum]

    def has_permission(self, permission: Enum) -> bool:
        return permission in self.permissions

    def has_any_permission(self, *permissions: Set[Enum]) -> bool:
        return any(map(self.has_permission, permissions))

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)
