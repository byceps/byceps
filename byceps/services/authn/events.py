"""
byceps.services.authn.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from byceps.services.core.events import BaseEvent, EventSite
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class UserAuthenticationEvent(BaseEvent):
    user: User


@dataclass(frozen=True, kw_only=True)
class PasswordUpdatedEvent(UserAuthenticationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagEvent(UserAuthenticationEvent):
    tag_id: UUID
    identifier: str


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagCreatedEvent(UserIdentityTagEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagDeletedEvent(UserIdentityTagEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserLoggedInEvent(UserAuthenticationEvent):
    ip_address: str | None
    site: EventSite | None


@dataclass(frozen=True, kw_only=True)
class UserLoggedInToAdminEvent(UserAuthenticationEvent):
    ip_address: str | None


@dataclass(frozen=True, kw_only=True)
class UserLoggedInToSiteEvent(UserAuthenticationEvent):
    ip_address: str | None
    site: EventSite
