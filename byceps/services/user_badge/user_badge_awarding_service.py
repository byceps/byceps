"""
byceps.services.user_badge.user_badge_awarding_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict

from sqlalchemy import select
import structlog

from byceps.database import db
from byceps.services.user import user_log_service
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result

from . import user_badge_domain_service
from .dbmodels import DbBadge, DbBadgeAwarding
from .errors import BadgeAwardingFailedError
from .events import UserBadgeAwardedEvent
from .models import (
    Badge,
    BadgeAwarding,
    BadgeID,
    QuantifiedBadgeAwarding,
)
from .user_badge_service import _db_entity_to_badge, get_badges


log = structlog.get_logger()


def award_badge_to_user(
    badge: Badge, awardee: User, *, initiator: User | None = None
) -> Result[
    tuple[BadgeAwarding, UserBadgeAwardedEvent], BadgeAwardingFailedError
]:
    """Award the badge to the user."""
    awarding_result = user_badge_domain_service.award_badge(
        badge, awardee, initiator=initiator
    )

    match awarding_result:
        case Err(e):
            log.error(
                'User badge awarding failed',
                badge_id=str(badge.id),
                badge_label=badge.label,
                awardee_id=str(awardee.id),
                awardee_screen_name=awardee.screen_name,
                initiator=initiator.screen_name if initiator else None,
                error_details=e.message,
            )
            return Err(e)

    awarding, event, log_entry = awarding_result.unwrap()

    _persist_awarding(awarding, log_entry)

    return Ok((awarding, event))


def _persist_awarding(
    awarding: BadgeAwarding,
    log_entry: UserLogEntry,
) -> None:
    db_awarding = DbBadgeAwarding(
        awarding.id, awarding.badge_id, awarding.awardee_id, awarding.awarded_at
    )
    db.session.add(db_awarding)

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def count_awardings() -> dict[BadgeID, int]:
    """Return the number of times each badge has been awarded.

    Because a badge can be awarded multiple times to a user, the number
    of awardings does not represent the number of awardees.
    """
    rows = (
        db.session.execute(
            select(DbBadge.id, db.func.count(DbBadgeAwarding.id))
            .outerjoin(DbBadgeAwarding)
            .group_by(DbBadge.id)
        )
        .tuples()
        .all()
    )

    return dict(rows)


def count_badge_awardings_to_user(badge_id: BadgeID, awardee_id: UserID) -> int:
    """Return the number of times the badge has been awarded to the user."""
    return (
        db.session.scalar(
            select(db.func.count(DbBadgeAwarding.id))
            .filter_by(badge_id=badge_id)
            .filter_by(awardee_id=awardee_id)
        )
        or 0
    )


def get_awardings_of_badge(badge_id: BadgeID) -> set[QuantifiedBadgeAwarding]:
    """Return the awardings of this badge."""
    rows = db.session.execute(
        select(
            DbBadgeAwarding.badge_id,
            DbBadgeAwarding.awardee_id,
            db.func.count(DbBadgeAwarding.badge_id),
        )
        .filter(DbBadgeAwarding.badge_id == badge_id)
        .group_by(DbBadgeAwarding.badge_id, DbBadgeAwarding.awardee_id)
    ).all()

    return {
        QuantifiedBadgeAwarding(
            badge_id=badge_id,
            awardee_id=awardee_id,
            quantity=quantity,
        )
        for badge_id, awardee_id, quantity in rows
    }


def get_badges_awarded_to_user(awardee_id: UserID) -> dict[Badge, int]:
    """Return all badges that have been awarded to the user (and how often)."""
    rows = (
        db.session.execute(
            select(
                DbBadgeAwarding.badge_id,
                db.func.count(DbBadgeAwarding.badge_id),
            )
            .filter(DbBadgeAwarding.awardee_id == awardee_id)
            .group_by(
                DbBadgeAwarding.badge_id,
            )
        )
        .tuples()
        .all()
    )

    badge_ids_with_awarding_quantity = {row[0]: row[1] for row in rows}

    badge_ids = set(badge_ids_with_awarding_quantity.keys())

    if badge_ids:
        db_badges = db.session.scalars(
            select(DbBadge).filter(DbBadge.id.in_(badge_ids))
        ).all()
    else:
        db_badges = []

    badges_with_awarding_quantity = {}
    for db_badge in db_badges:
        quantity = badge_ids_with_awarding_quantity[db_badge.id]
        badges_with_awarding_quantity[_db_entity_to_badge(db_badge)] = quantity

    return badges_with_awarding_quantity


def get_badges_awarded_to_users(
    awardee_ids: set[UserID], *, featured_only: bool = False
) -> dict[UserID, set[Badge]]:
    """Return all badges that have been awarded to the users, indexed
    by user ID.

    If `featured_only` is `True`, only return featured badges.
    """
    if not awardee_ids:
        return {}

    awardings = db.session.scalars(
        select(DbBadgeAwarding).filter(
            DbBadgeAwarding.awardee_id.in_(awardee_ids)
        )
    ).all()

    badge_ids = {awarding.badge_id for awarding in awardings}
    badges = get_badges(badge_ids, featured_only=featured_only)
    badges_by_id = {badge.id: badge for badge in badges}

    badges_by_awardee_id: dict[UserID, set[Badge]] = defaultdict(set)
    for awarding in awardings:
        badge = badges_by_id.get(awarding.badge_id)
        if badge:
            badges_by_awardee_id[awarding.awardee_id].add(badge)

    return dict(badges_by_awardee_id)
