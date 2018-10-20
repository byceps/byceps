"""
byceps.services.authentication.session.models.current_user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Optional, Set, Union

from .....services.orga_team import service as orga_team_service
from .....services.user.models.user import AnonymousUser, User as DbUser
from .....services.user import service as user_service
from .....services.user.transfer.models import User
from .....services.user_avatar import service as user_avatar_service
from .....typing import PartyID


class CurrentUser:

    def __init__(self, user: Union[AnonymousUser, DbUser], is_anonymous: bool,
                 avatar_url: Optional[str], is_orga: bool,
                 permissions: Set[Enum]) -> None:
        self._user = user

        self.id = user.id
        self.screen_name = user.screen_name if not is_anonymous else None
        self.is_active = user.enabled if not is_anonymous else False
        self.is_anonymous = is_anonymous

        self.avatar_url = avatar_url
        self.is_orga = is_orga

        self.permissions = permissions

    @classmethod
    def create_anonymous(self) -> 'CurrentUser':
        user = user_service.get_anonymous_user()
        is_anonymous = True
        avatar_url = None
        is_orga = False
        permissions = frozenset()

        return CurrentUser(user, is_anonymous, avatar_url, is_orga, permissions)

    @classmethod
    def create_from_user(self, user: DbUser, permissions: Set[Enum],
                         *, party_id: Optional[PartyID]=None
                        ) -> 'CurrentUser':
        is_anonymous = False
        avatar_url = user_avatar_service.get_avatar_url_for_user(user.id)
        if party_id is not None:
            is_orga = orga_team_service.is_orga_for_party(user.id, party_id)
        else:
            is_orga = False

        return CurrentUser(user, is_anonymous, avatar_url, is_orga, permissions)

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

    def __hash__(self) -> str:
        return hash(self._user)
