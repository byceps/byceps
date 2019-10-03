"""
byceps.services.authentication.session.models.current_user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Optional, Set, Union

from .....services.user.models.user import AnonymousUser
from .....services.user import service as user_service
from .....services.user.transfer.models import User
from .....typing import PartyID


class CurrentUser:

    def __init__(self, user: Union[AnonymousUser, User], is_anonymous: bool,
                 permissions: Set[Enum]) -> None:
        self.id = user.id
        self.screen_name = user.screen_name if not is_anonymous else None
        self.is_active = not is_anonymous
        self.is_anonymous = is_anonymous

        self.deleted = user.deleted
        self.avatar_url = user.avatar_url
        self.is_orga = user.is_orga

        self.permissions = permissions

    @classmethod
    def create_anonymous(self) -> CurrentUser:
        user = user_service.get_anonymous_user()
        is_anonymous = True
        permissions = frozenset()

        return CurrentUser(user, is_anonymous, permissions)

    @classmethod
    def create_from_user(self, user: User, permissions: Set[Enum]
                        ) -> CurrentUser:
        is_anonymous = False

        return CurrentUser(user, is_anonymous, permissions)

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
