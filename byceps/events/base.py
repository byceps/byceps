"""
byceps.events.base
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Self

from byceps.services.brand.models import Brand, BrandID
from byceps.services.party.models import Party, PartyID
from byceps.services.site.models import Site, SiteID
from byceps.services.user.models.user import User, UserID


@dataclass(frozen=True)
class EventBrand:
    id: BrandID
    title: str

    @classmethod
    def from_brand(cls, brand: Brand) -> Self:
        return cls(
            id=brand.id,
            title=brand.title,
        )


@dataclass(frozen=True)
class EventParty:
    id: PartyID
    title: str

    @classmethod
    def from_party(cls, party: Party) -> Self:
        return cls(
            id=party.id,
            title=party.title,
        )


@dataclass(frozen=True)
class EventSite:
    id: SiteID
    title: str

    @classmethod
    def from_site(cls, site: Site) -> Self:
        return cls(
            id=site.id,
            title=site.title,
        )


@dataclass(frozen=True)
class EventUser:
    id: UserID
    screen_name: str | None

    @classmethod
    def from_user(cls, user: User) -> Self:
        return cls(
            id=user.id,
            screen_name=user.screen_name,
        )


@dataclass(frozen=True)
class _BaseEvent:
    occurred_at: datetime
    initiator: EventUser | None
