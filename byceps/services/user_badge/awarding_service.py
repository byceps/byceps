"""
byceps.services.user_badge.awarding_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import Optional

from ...database import db
from ...events.user_badge import UserBadgeAwarded
from ...typing import UserID

from ..user import event_service as user_event_service, service as user_service
from ..user.transfer.models import User

from .badge_service import _db_entity_to_badge, get_badge, get_badges
from .dbmodels.awarding import BadgeAwarding as DbBadgeAwarding
from .dbmodels.badge import Badge as DbBadge
from .transfer.models import (
    Badge,
    BadgeAwarding,
    BadgeID,
    QuantifiedBadgeAwarding,
)


def award_badge_to_user(
    badge_id: BadgeID, user_id: UserID, *, initiator_id: Optional[UserID] = None
) -> tuple[BadgeAwarding, UserBadgeAwarded]:
    """Award the badge to the user."""
    badge = get_badge(badge_id)
    user = user_service.get_user(user_id)
    awarded_at = datetime.utcnow()

    initiator: Optional[User]
    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    awarding = DbBadgeAwarding(badge_id, user_id, awarded_at=awarded_at)
    db.session.add(awarding)

    user_event_data = {'badge_id': str(badge_id)}
    if initiator_id:
        user_event_data['initiator_id'] = str(initiator_id)
    user_event = user_event_service.build_event(
        'user-badge-awarded', user_id, user_event_data, occurred_at=awarded_at
    )
    db.session.add(user_event)

    db.session.commit()

    awarding_dto = _db_entity_to_badge_awarding(awarding)

    event = UserBadgeAwarded(
        occurred_at=awarded_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        user_id=user_id,
        user_screen_name=user.screen_name,
        badge_id=badge_id,
        badge_label=badge.label,
    )

    return awarding_dto, event


def count_awardings() -> dict[BadgeID, int]:
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


def get_awardings_of_badge(badge_id: BadgeID) -> set[QuantifiedBadgeAwarding]:
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


def get_badges_awarded_to_user(user_id: UserID) -> dict[Badge, int]:
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
        badges = db.session \
            .query(DbBadge) \
            .filter(DbBadge.id.in_(badge_ids)) \
            .all()
    else:
        badges = []

    badges_with_awarding_quantity = {}
    for badge in badges:
        quantity = badge_ids_with_awarding_quantity[badge.id]
        badges_with_awarding_quantity[_db_entity_to_badge(badge)] = quantity

    return badges_with_awarding_quantity


def get_badges_awarded_to_users(
    user_ids: set[UserID], *, featured_only: bool = False
) -> dict[UserID, set[Badge]]:
    """Return all badges that have been awarded to the users, indexed
    by user ID.

    If `featured_only` is `True`, only return featured badges.
    """
    if not user_ids:
        return {}

    awardings = db.session \
        .query(DbBadgeAwarding) \
        .filter(DbBadgeAwarding.user_id.in_(user_ids)) \
        .all()

    badge_ids = {awarding.badge_id for awarding in awardings}
    badges = get_badges(badge_ids, featured_only=featured_only)
    badges_by_id = {badge.id: badge for badge in badges}

    badges_by_user_id: dict[UserID, set[Badge]] = defaultdict(set)
    for awarding in awardings:
        badge = badges_by_id.get(awarding.badge_id)
        if badge:
            badges_by_user_id[awarding.user_id].add(badge)

    return dict(badges_by_user_id)


def _db_entity_to_badge_awarding(entity: DbBadgeAwarding) -> BadgeAwarding:
    return BadgeAwarding(
        entity.id,
        entity.badge_id,
        entity.user_id,
        entity.awarded_at
    )
