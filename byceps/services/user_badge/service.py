"""
byceps.services.user_badge.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Set

from .models.badge import Badge as DbBadge
from .transfer.models import Badge, BadgeID


def find_badge(badge_id: BadgeID) -> Optional[Badge]:
    """Return the badge with that id, or `None` if not found."""
    badge = DbBadge.query.get(badge_id)

    if badge is None:
        return None

    return _db_entity_to_badge(badge)


def find_badge_by_slug(slug: str) -> Optional[Badge]:
    """Return the badge with that slug, or `None` if not found."""
    badge = DbBadge.query \
        .filter_by(slug=slug) \
        .one_or_none()

    if badge is None:
        return None

    return _db_entity_to_badge(badge)


def get_badges(
    badge_ids: Set[BadgeID], *, featured_only: bool = False
) -> Set[Badge]:
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


def get_all_badges() -> Set[Badge]:
    """Return all badges."""
    badges = DbBadge.query.all()

    return {_db_entity_to_badge(badge) for badge in badges}


def _db_entity_to_badge(entity: DbBadge) -> Badge:
    image_url_path = f'/data/global/users/badges/{entity.image_filename}'

    return Badge(
        entity.id,
        entity.brand_id,
        entity.slug,
        entity.label,
        entity.description,
        image_url_path,
        entity.featured,
    )
