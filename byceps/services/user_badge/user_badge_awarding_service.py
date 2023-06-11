"""
byceps.services.user_badge.user_badge_awarding_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.events.user_badge import UserBadgeAwardedEvent
from byceps.services.user import user_log_service, user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID

from .dbmodels.awarding import DbBadgeAwarding
from .dbmodels.badge import DbBadge
from .models import (
    Badge,
    BadgeAwarding,
    BadgeID,
    QuantifiedBadgeAwarding,
)
from .user_badge_service import _db_entity_to_badge, get_badge, get_badges


def award_badge_to_user(
    badge_id: BadgeID, awardee_id: UserID, *, initiator_id: UserID | None = None
) -> tuple[BadgeAwarding, UserBadgeAwardedEvent]:
    """Award the badge to the user."""
    badge = get_badge(badge_id)
    awardee = user_service.get_user(awardee_id)
    awarded_at = datetime.utcnow()

    initiator: User | None
    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    awarding = DbBadgeAwarding(badge_id, awardee_id, awarded_at=awarded_at)
    db.session.add(awarding)

    user_log_entry_data = {'badge_id': str(badge_id)}
    if initiator_id:
        user_log_entry_data['initiator_id'] = str(initiator_id)
    user_log_entry = user_log_service.build_entry(
        'user-badge-awarded',
        awardee_id,
        user_log_entry_data,
        occurred_at=awarded_at,
    )
    db.session.add(user_log_entry)

    db.session.commit()

    awarding_dto = _db_entity_to_badge_awarding(awarding)

    event = UserBadgeAwardedEvent(
        occurred_at=awarded_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        badge_id=badge_id,
        badge_label=badge.label,
        awardee_id=awardee_id,
        awardee_screen_name=awardee.screen_name,
    )

    return awarding_dto, event


def count_awardings() -> dict[BadgeID, int]:
    """Return the number of times each badge has been awarded.

    Because a badge can be awarded multiple times to a user, the number
    of awardings does not represent the number of awardees.
    """
    rows = db.session.execute(
        select(DbBadge.id, db.func.count(DbBadgeAwarding.id))
        .outerjoin(DbBadgeAwarding)
        .group_by(DbBadge.id)
    ).all()

    return dict(rows)


def get_awardings_of_badge(badge_id: BadgeID) -> set[QuantifiedBadgeAwarding]:
    """Return the awardings of this badge."""
    rows = db.session.execute(
        select(
            DbBadgeAwarding.badge_id,
            DbBadgeAwarding.user_id,
            db.func.count(DbBadgeAwarding.badge_id),
        )
        .filter(DbBadgeAwarding.badge_id == badge_id)
        .group_by(DbBadgeAwarding.badge_id, DbBadgeAwarding.user_id)
    ).all()

    return {
        QuantifiedBadgeAwarding(badge_id, user_id, quantity)
        for badge_id, user_id, quantity in rows
    }


def get_badges_awarded_to_user(user_id: UserID) -> dict[Badge, int]:
    """Return all badges that have been awarded to the user (and how often)."""
    rows = db.session.execute(
        select(
            DbBadgeAwarding.badge_id, db.func.count(DbBadgeAwarding.badge_id)
        )
        .filter(DbBadgeAwarding.user_id == user_id)
        .group_by(
            DbBadgeAwarding.badge_id,
        )
    ).all()

    badge_ids_with_awarding_quantity = {row[0]: row[1] for row in rows}

    badge_ids = set(badge_ids_with_awarding_quantity.keys())

    if badge_ids:
        badges = db.session.scalars(
            select(DbBadge).filter(DbBadge.id.in_(badge_ids))
        ).all()
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

    awardings = db.session.scalars(
        select(DbBadgeAwarding).filter(DbBadgeAwarding.user_id.in_(user_ids))
    ).all()

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
        id=entity.id,
        badge_id=entity.badge_id,
        user_id=entity.user_id,
        awarded_at=entity.awarded_at,
    )
