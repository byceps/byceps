"""
byceps.services.user_badge.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrs

from ....typing import BrandID, UserID


BadgeID = NewType('BadgeID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Badge:
    id: BadgeID
    brand_id: BrandID
    slug: str
    label: str
    description: str
    image_url_path: str
    featured: bool


@attrs(auto_attribs=True, frozen=True, slots=True)
class BadgeAwarding:
    id: UUID
    badge_id: BadgeID
    user_id: UserID
    awarded_at: datetime


@attrs(auto_attribs=True, frozen=True, slots=True)
class QuantifiedBadgeAwarding:
    badge_id: BadgeID
    user_id: UserID
    quantity: int
