"""
byceps.services.authentication.session.models.current_user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Set

from .....services.user.models.user import User as DbUser
from .....services.user.transfer.models import User


class CurrentUser:

    def __init__(self, user: DbUser, avatar_url: str) -> None:
        self._user = user

        self.id = user.id
        self.screen_name = user.screen_name if not user.is_anonymous else None
        self.is_active = user.is_active
        self.is_anonymous = user.is_anonymous

        self.avatar_url = avatar_url

    @property
    def is_orga(self) -> bool:
        return self._user.is_orga

    def has_permission(self, permission: Enum) -> bool:
        return self._user.has_permission(permission)

    def has_any_permission(self, *permissions: Set[Enum]) -> bool:
        return self._user.has_any_permission(*permissions)

    def to_dto(self) -> User:
        is_orga = False  # Information is deliberately not obtained here.

        return User(
            self.id,
            self.screen_name,
            self._user.suspended,
            self._user.deleted,
            self.avatar_url,
            is_orga,
        )

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)

    def __hash__(self) -> str:
        return hash(self._user)
