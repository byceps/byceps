"""
byceps.services.user_badge.badge_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db
from ...typing import BrandID

from .dbmodels.badge import Badge as DbBadge
from .transfer.models import Badge, BadgeID


def create_badge(
    slug: str,
    label: str,
    image_filename: str,
    *,
    description: Optional[str] = None,
    brand_id: Optional[BrandID] = None,
    featured: bool = False,
) -> Badge:
    """Create a badge."""
    badge = DbBadge(
        slug,
        label,
        image_filename,
        description=description,
        brand_id=brand_id,
        featured=featured,
    )

    db.session.add(badge)
    db.session.commit()

    return _db_entity_to_badge(badge)


def update_badge(
    badge_id: BadgeID,
    slug: str,
    label: str,
    description: Optional[str],
    image_filename: str,
    brand_id: Optional[BrandID],
    featured: bool,
) -> Badge:
    """Update a badge."""
    badge = DbBadge.query.get(badge_id)
    if not badge:
        raise ValueError(f'Unknown badge ID: "{badge_id}"')

    badge.slug = slug
    badge.label = label
    badge.description = description
    badge.image_filename = image_filename
    badge.brand_id = brand_id
    badge.featured = featured

    db.session.commit()

    return _db_entity_to_badge(badge)


def delete_badge(badge_id: BadgeID) -> None:
    """Delete a badge."""
    db.session.query(DbBadge) \
        .filter_by(id=badge_id) \
        .delete()

    db.session.commit()


def find_badge(badge_id: BadgeID) -> Optional[Badge]:
    """Return the badge with that id, or `None` if not found."""
    badge = DbBadge.query.get(badge_id)

    if badge is None:
        return None

    return _db_entity_to_badge(badge)


def get_badge(badge_id: BadgeID) -> Badge:
    """Return the badge with that id, or raise an exception."""
    badge = find_badge(badge_id)

    if badge is None:
        raise ValueError(f'Unknown badge ID "{badge_id}"')

    return badge


def find_badge_by_slug(slug: str) -> Optional[Badge]:
    """Return the badge with that slug, or `None` if not found."""
    badge = DbBadge.query \
        .filter_by(slug=slug) \
        .one_or_none()

    if badge is None:
        return None

    return _db_entity_to_badge(badge)


def get_badges(
    badge_ids: set[BadgeID], *, featured_only: bool = False
) -> set[Badge]:
    """Return the badges with those IDs.

    If `featured_only` is `True`, only return featured badges.
    """
    if not badge_ids:
        return set()

    query = DbBadge.query \
        .filter(DbBadge.id.in_(badge_ids))

    if featured_only:
        query = query.filter_by(featured=True)

    badges = query.all()

    return {_db_entity_to_badge(badge) for badge in badges}


def get_all_badges() -> set[Badge]:
    """Return all badges."""
    badges = DbBadge.query.all()

    return {_db_entity_to_badge(badge) for badge in badges}


def _db_entity_to_badge(entity: DbBadge) -> Badge:
    image_url_path = f'/data/global/users/badges/{entity.image_filename}'

    return Badge(
        entity.id,
        entity.slug,
        entity.label,
        entity.description,
        entity.image_filename,
        image_url_path,
        entity.brand_id,
        entity.featured,
    )
