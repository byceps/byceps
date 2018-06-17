"""
byceps.services.user_badge.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import BrandID, UserID


BadgeID = NewType('BadgeID', UUID)


@attrs(frozen=True, slots=True)
class Badge:
    id = attrib(type=BadgeID)
    brand_id = attrib(type=BrandID)
    slug = attrib(type=str)
    label = attrib(type=str)
    description = attrib(type=str)
    image_url = attrib(type=str)
    featured = attrib(type=bool)


@attrs(frozen=True, slots=True)
class BadgeAwarding:
    id = attrib(type=UUID)
    badge_id = attrib(type=BadgeID)
    user_id = attrib(type=UserID)
    awarded_at = attrib(type=datetime)
