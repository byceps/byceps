"""
byceps.services.core.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Self

from byceps.services.brand.models import Brand, BrandID
from byceps.services.party.models import Party, PartyID
from byceps.services.site.models import Site, SiteID
from byceps.services.user.models import User


@dataclass(frozen=True, kw_only=True)
class EventBrand:
    id: BrandID
    title: str

    @classmethod
    def from_brand(cls, brand: Brand) -> Self:
        return cls(
            id=brand.id,
            title=brand.title,
        )


@dataclass(frozen=True, kw_only=True)
class EventParty:
    id: PartyID
    title: str

    @classmethod
    def from_party(cls, party: Party) -> Self:
        return cls(
            id=party.id,
            title=party.title,
        )


@dataclass(frozen=True, kw_only=True)
class EventSite:
    id: SiteID
    title: str

    @classmethod
    def from_site(cls, site: Site) -> Self:
        return cls(
            id=site.id,
            title=site.title,
        )


@dataclass(frozen=True, kw_only=True)
class BaseEvent:
    occurred_at: datetime
    initiator: User | None
