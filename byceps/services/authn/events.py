"""
byceps.services.authn.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventSite, EventUser


@dataclass(frozen=True, kw_only=True)
class PasswordUpdatedEvent(_BaseEvent):
    user: EventUser


@dataclass(frozen=True, kw_only=True)
class _UserIdentityTagEvent(_BaseEvent):
    identifier: str
    user: EventUser


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagCreatedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserIdentityTagDeletedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserLoggedInEvent(_BaseEvent):
    site: EventSite | None
