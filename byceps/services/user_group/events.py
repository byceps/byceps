"""
byceps.services.user_group.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent
from byceps.services.user.models import User
from byceps.services.user_group.models import UserGroup


@dataclass(frozen=True, kw_only=True)
class UserGroupCreatedEvent(BaseEvent):
    group: UserGroup


@dataclass(frozen=True, kw_only=True)
class UserGroupDeletedEvent(BaseEvent):
    group: UserGroup


@dataclass(frozen=True, kw_only=True)
class UserGroupMemberAddedEvent(BaseEvent):
    group: UserGroup
    member: User


@dataclass(frozen=True, kw_only=True)
class UserGroupMemberRemovedEvent(BaseEvent):
    group: UserGroup
    member: User
