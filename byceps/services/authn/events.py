"""
byceps.services.authn.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent, EventSite
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class PasswordUpdatedEvent(BaseEvent):
    user: User


@dataclass(frozen=True, kw_only=True)
class _UserIdentityTagEvent(BaseEvent):
    identifier: str
    user: User


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagCreatedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagDeletedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserLoggedInEvent(BaseEvent):
    user: User
    site: EventSite | None
