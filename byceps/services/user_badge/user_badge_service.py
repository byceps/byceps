"""
byceps.services.user_badge.user_badge_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.brand.models import BrandID

from .dbmodels import DbBadge
from .models import Badge, BadgeID


def create_badge(
    slug: str,
    label: str,
    image_filename: str,
    *,
    description: str | None = None,
    brand_id: BrandID | None = None,
    featured: bool = False,
) -> Badge:
    """Create a badge."""
    db_badge = DbBadge(
        slug,
        label,
        image_filename,
        description=description,
        brand_id=brand_id,
        featured=featured,
    )

    db.session.add(db_badge)
    db.session.commit()

    return _db_entity_to_badge(db_badge)


def update_badge(
    badge_id: BadgeID,
    slug: str,
    label: str,
    description: str | None,
    image_filename: str,
    brand_id: BrandID | None,
    featured: bool,
) -> Badge:
    """Update a badge."""
    db_badge = db.session.get(DbBadge, badge_id)
    if not db_badge:
        raise ValueError(f'Unknown badge ID: "{badge_id}"')

    db_badge.slug = slug
    db_badge.label = label
    db_badge.description = description
    db_badge.image_filename = image_filename
    db_badge.brand_id = brand_id
    db_badge.featured = featured

    db.session.commit()

    return _db_entity_to_badge(db_badge)


def delete_badge(badge_id: BadgeID) -> None:
    """Delete a badge."""
    db.session.execute(delete(DbBadge).filter_by(id=badge_id))
    db.session.commit()


def find_badge(badge_id: BadgeID) -> Badge | None:
    """Return the badge with that id, or `None` if not found."""
    db_badge = db.session.get(DbBadge, badge_id)

    if db_badge is None:
        return None

    return _db_entity_to_badge(db_badge)


def get_badge(badge_id: BadgeID) -> Badge:
    """Return the badge with that id, or raise an exception."""
    badge = find_badge(badge_id)

    if badge is None:
        raise ValueError(f'Unknown badge ID "{badge_id}"')

    return badge


def find_badge_by_slug(slug: str) -> Badge | None:
    """Return the badge with that slug, or `None` if not found."""
    db_badge = db.session.scalars(
        select(DbBadge).filter_by(slug=slug)
    ).one_or_none()

    if db_badge is None:
        return None

    return _db_entity_to_badge(db_badge)


def get_badges(
    badge_ids: set[BadgeID], *, featured_only: bool = False
) -> set[Badge]:
    """Return the badges with those IDs.

    If `featured_only` is `True`, only return featured badges.
    """
    if not badge_ids:
        return set()

    stmt = select(DbBadge).filter(DbBadge.id.in_(badge_ids))

    if featured_only:
        stmt = stmt.filter_by(featured=True)

    db_badges = db.session.scalars(stmt).all()

    return {_db_entity_to_badge(db_badge) for db_badge in db_badges}


def get_all_badges() -> set[Badge]:
    """Return all badges."""
    db_badges = db.session.scalars(select(DbBadge)).all()

    return {_db_entity_to_badge(db_badge) for db_badge in db_badges}


def _db_entity_to_badge(db_badge: DbBadge) -> Badge:
    image_url_path = f'/data/global/users/badges/{db_badge.image_filename}'

    return Badge(
        db_badge.id,
        db_badge.slug,
        db_badge.label,
        db_badge.description,
        db_badge.image_filename,
        image_url_path,
        db_badge.brand_id,
        db_badge.featured,
    )
