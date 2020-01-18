"""
byceps.services.user_badge.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict
from typing import Dict, Optional, Set

from ...database import db
from ...typing import UserID

from .models.awarding import BadgeAwarding as DbBadgeAwarding
from .models.badge import Badge as DbBadge
from .transfer.models import Badge, BadgeID, QuantifiedBadgeAwarding


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


def get_badges_for_user(user_id: UserID) -> Dict[Badge, int]:
    """Return all badges that have been awarded to the user (and how often)."""
    rows = db.session \
        .query(
            DbBadgeAwarding.badge_id,
            db.func.count(DbBadgeAwarding.badge_id)
        ) \
        .filter(DbBadgeAwarding.user_id == user_id) \
        .group_by(
            DbBadgeAwarding.badge_id,
        ) \
        .all()

    badge_ids_with_awarding_quantity = {row[0]: row[1] for row in rows}

    badge_ids = set(badge_ids_with_awarding_quantity.keys())

    if badge_ids:
        badges = DbBadge.query \
            .filter(DbBadge.id.in_(badge_ids)) \
            .all()
    else:
        badges = []

    badges_with_awarding_quantity = {}
    for badge in badges:
        quantity = badge_ids_with_awarding_quantity[badge.id]
        badges_with_awarding_quantity[_db_entity_to_badge(badge)] = quantity

    return badges_with_awarding_quantity


def get_badges_for_users(
    user_ids: Set[UserID], *, featured_only: bool = False
) -> Dict[UserID, Set[Badge]]:
    """Return all badges that have been awarded to the users, indexed
    by user ID.

    If `featured_only` is `True`, only return featured badges.
    """
    if not user_ids:
        return {}

    awardings = DbBadgeAwarding.query \
        .filter(DbBadgeAwarding.user_id.in_(user_ids)) \
        .all()

    badge_ids = {awarding.badge_id for awarding in awardings}
    badges = get_badges(badge_ids, featured_only=featured_only)
    badges_by_id = {badge.id: badge for badge in badges}

    badges_by_user_id: Dict[UserID, Set[Badge]] = defaultdict(set)
    for awarding in awardings:
        badge = badges_by_id.get(awarding.badge_id)
        if badge:
            badges_by_user_id[awarding.user_id].add(badge)

    return dict(badges_by_user_id)


def get_all_badges() -> Set[Badge]:
    """Return all badges."""
    badges = DbBadge.query.all()

    return {_db_entity_to_badge(badge) for badge in badges}


def count_awardings() -> Dict[BadgeID, int]:
    """Return the number of times each badge has been awarded.

    Because a badge can be awarded multiple times to a user, the number
    of awardings does not represent the number of awardees.
    """
    rows = db.session \
        .query(
            DbBadge.id,
            db.func.count(DbBadgeAwarding.id)
        ) \
        .outerjoin(DbBadgeAwarding) \
        .group_by(DbBadge.id) \
        .all()

    return {badge_id: count for badge_id, count in rows}


def get_awardings_of_badge(badge_id: BadgeID) -> Set[QuantifiedBadgeAwarding]:
    """Return the awardings of this badge."""
    rows = db.session \
        .query(
            DbBadgeAwarding.badge_id,
            DbBadgeAwarding.user_id,
            db.func.count(DbBadgeAwarding.badge_id)
        ) \
        .filter(DbBadgeAwarding.badge_id == badge_id) \
        .group_by(
            DbBadgeAwarding.badge_id,
            DbBadgeAwarding.user_id
        ) \
        .all()

    return {
        QuantifiedBadgeAwarding(badge_id, user_id, quantity)
        for badge_id, user_id, quantity in rows
    }


def _db_entity_to_badge(entity: DbBadge) -> Badge:
    image_url_path = f'/global/users/badges/{entity.image_filename}'

    return Badge(
        entity.id,
        entity.brand_id,
        entity.slug,
        entity.label,
        entity.description,
        image_url_path,
        entity.featured,
    )
