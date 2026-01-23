"""
byceps.services.user_badge.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.brand.models import BrandID
from byceps.services.user.models import UserID


BadgeID = NewType('BadgeID', UUID)


@dataclass(frozen=True, kw_only=True)
class Badge:
    id: BadgeID
    slug: str
    label: str
    description: str | None
    image_filename: str
    image_url_path: str
    brand_id: BrandID | None
    featured: bool


@dataclass(frozen=True, kw_only=True)
class BadgeAwarding:
    id: UUID
    badge_id: BadgeID
    awardee_id: UserID
    awarded_at: datetime


@dataclass(frozen=True, kw_only=True)
class QuantifiedBadgeAwarding:
    badge_id: BadgeID
    awardee_id: UserID
    quantity: int
