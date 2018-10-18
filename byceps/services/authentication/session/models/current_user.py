"""
byceps.services.authentication.session.models.current_user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Optional, Set, Union

from .....services.user.models.user import AnonymousUser, User as DbUser
from .....services.user import service as user_service
from .....services.user.transfer.models import User


class CurrentUser:

    def __init__(self, user: Union[AnonymousUser, DbUser], is_anonymous: bool,
                 avatar_url: Optional[str], permissions: Set[Enum]) -> None:
        self._user = user

        self.id = user.id
        self.screen_name = user.screen_name if not is_anonymous else None
        self.is_active = user.enabled if not is_anonymous else False
        self.is_anonymous = is_anonymous

        self.avatar_url = avatar_url

        self.permissions = permissions

    @classmethod
    def create_anonymous(self) -> 'CurrentUser':
        user = user_service.get_anonymous_user()
        is_anonymous = True
        avatar_url = None
        permissions = frozenset()

        return CurrentUser(user, is_anonymous, avatar_url, permissions)

    @classmethod
    def create_from_user(self, user: DbUser, avatar_url: Optional[str],
                         permissions: Set[Enum]) -> 'CurrentUser':
        is_anonymous = False

        return CurrentUser(user, is_anonymous, avatar_url, permissions)

    @property
    def is_orga(self) -> bool:
        return self._user.is_orga

    def has_permission(self, permission: Enum) -> bool:
        return permission in self.permissions

    def has_any_permission(self, *permissions: Set[Enum]) -> bool:
        return any(map(self.has_permission, permissions))

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
