"""
byceps.services.user_badge.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import BrandID

from .models.badge import Badge as DbBadge
from .service import _db_entity_to_badge
from .transfer.models import Badge, BadgeID


def create_badge(
    slug: str,
    label: str,
    image_filename: str,
    *,
    brand_id: Optional[BrandID] = None,
    description: Optional[str] = None,
    featured: bool = False,
) -> Badge:
    """Create a badge."""
    badge = DbBadge(
        slug,
        label,
        image_filename,
        brand_id=brand_id,
        description=description,
        featured=featured,
    )

    db.session.add(badge)
    db.session.commit()

    return _db_entity_to_badge(badge)


def update_badge(
    badge_id: BadgeID,
    brand_id: Optional[BrandID],
    slug: str,
    label: str,
    description: Optional[str],
    image_filename: str,
    featured: bool,
) -> Badge:
    """Update a badge."""
    badge = DbBadge.query.get(badge_id)
    if not badge:
        raise ValueError(f'Unknown badge ID: "{badge_id}"')

    badge.brand_id = brand_id
    badge.slug = slug
    badge.label = label
    badge.description = description
    badge.image_filename = image_filename
    badge.featured = featured

    db.session.commit()

    return _db_entity_to_badge(badge)


def delete_badge(badge_id: BadgeID) -> None:
    """Delete a badge."""
    db.session.query(DbBadge) \
        .filter_by(id=badge_id) \
        .delete()

    db.session.commit()
