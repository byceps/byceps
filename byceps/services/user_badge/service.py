"""
byceps.services.user_badge.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict
from typing import Dict, Optional, Set

from ...database import db
from ...typing import BrandID, UserID

from .models.awarding import BadgeAwarding, BadgeAwardingTuple, \
    QuantifiedBadgeAwardingTuple
from .models.badge import Badge, BadgeID, BadgeTuple


def create_badge(label: str, image_filename: str, *,
                 brand_id: Optional[BrandID]=None,
                 description: Optional[str]=None,
                 is_featured: bool=False) -> BadgeTuple:
    """Introduce a new badge."""
    badge = Badge(label, image_filename, brand_id=brand_id,
                  description=description, is_featured=is_featured)

    db.session.add(badge)
    db.session.commit()

    return badge.to_tuple()


def find_badge(badge_id: BadgeID) -> Optional[BadgeTuple]:
    """Return the badge with that id, or `None` if not found."""
    badge = Badge.query.get(badge_id)

    if badge is None:
        return None

    return badge.to_tuple()


def get_badges(badge_ids: Set[BadgeID], *, featured_only: bool=False
              ) -> Set[BadgeTuple]:
    """Return the badges with those IDs.

    If `featured_only` is `True`, only return featured badges.
    """
    if not badge_ids:
        return set()

    query = Badge.query \
        .filter(Badge.id.in_(badge_ids))

    if featured_only:
        query = query.filter_by(is_featured=True)

    badges = query.all()

    return {badge.to_tuple() for badge in badges}


def get_badges_for_user(user_id: UserID) -> Dict[BadgeTuple, int]:
    """Return all badges that have been awarded to the user (and how often)."""
    rows = db.session \
        .query(
            BadgeAwarding.badge_id,
            db.func.count(BadgeAwarding.badge_id)
        ) \
        .filter(BadgeAwarding.user_id == user_id) \
        .group_by(
            BadgeAwarding.badge_id,
        ) \
        .all()

    badge_ids_with_awarding_quantity = {row[0]: row[1] for row in rows}

    badge_ids = set(badge_ids_with_awarding_quantity.keys())

    badges = Badge.query \
        .filter(Badge.id.in_(badge_ids)) \
        .all()

    badges_with_awarding_quantity = {}
    for badge in badges:
        quantity = badge_ids_with_awarding_quantity[badge.id]
        badges_with_awarding_quantity[badge.to_tuple()] = quantity

    return badges_with_awarding_quantity


def get_badges_for_users(user_ids: Set[UserID], *, featured_only: bool=False
                        ) -> Dict[UserID, Set[BadgeTuple]]:
    """Return all badges that have been awarded to the users, indexed
    by user ID.

    If `featured_only` is `True`, only return featured badges.
    """
    if not user_ids:
        return {}

    awardings = BadgeAwarding.query \
        .filter(BadgeAwarding.user_id.in_(user_ids)) \
        .all()

    badge_ids = {awarding.badge_id for awarding in awardings}
    badges = get_badges(badge_ids, featured_only=featured_only)
    badges_by_id = {badge.id: badge for badge in badges}

    badges_by_user_id = defaultdict(set)  # type: Dict[UserID, Set[BadgeTuple]]
    for awarding in awardings:
        badge = badges_by_id.get(awarding.badge_id)
        if badge:
            badges_by_user_id[awarding.user_id].add(badge)

    return dict(badges_by_user_id)


def get_all_badges() -> Set[BadgeTuple]:
    """Return all badges."""
    badges = Badge.query.all()

    return {badge.to_tuple() for badge in badges}


def award_badge_to_user(badge_id: BadgeID, user_id: UserID) \
                        -> BadgeAwardingTuple:
    """Award the badge to the user."""
    awarding = BadgeAwarding(badge_id, user_id)

    db.session.add(awarding)
    db.session.commit()

    return awarding.to_tuple()


def get_awardings_of_badge(badge_id: BadgeID) \
                           -> Set[QuantifiedBadgeAwardingTuple]:
    """Return the awardings (user and date) of this badge."""
    rows = db.session \
        .query(
            BadgeAwarding.badge_id,
            BadgeAwarding.user_id,
            db.func.count(BadgeAwarding.badge_id)
        ) \
        .filter(BadgeAwarding.badge_id == badge_id) \
        .group_by(
            BadgeAwarding.badge_id,
            BadgeAwarding.user_id
        ) \
        .all()

    return {QuantifiedBadgeAwardingTuple(badge_id, user_id, quantity)
            for badge_id, user_id, quantity in rows}
