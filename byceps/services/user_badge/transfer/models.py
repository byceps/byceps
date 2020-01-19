"""
byceps.services.user_badge.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from ....typing import BrandID, UserID


BadgeID = NewType('BadgeID', UUID)


@dataclass(frozen=True)
class Badge:
    id: BadgeID
    brand_id: BrandID
    slug: str
    label: str
    description: str
    image_url_path: str
    featured: bool


@dataclass(frozen=True)
class BadgeAwarding:
    id: UUID
    badge_id: BadgeID
    user_id: UserID
    awarded_at: datetime


@dataclass(frozen=True)
class QuantifiedBadgeAwarding:
    badge_id: BadgeID
    user_id: UserID
    quantity: int
