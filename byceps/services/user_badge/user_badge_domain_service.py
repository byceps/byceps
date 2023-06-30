"""
byceps.services.user_badge.user_badge_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from byceps.database import generate_uuid7
from byceps.events.user_badge import UserBadgeAwardedEvent
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User

from .models import Badge, BadgeAwarding


def award_badge(
    badge: Badge, awardee: User, *, initiator: User | None = None
) -> tuple[BadgeAwarding, UserBadgeAwardedEvent, UserLogEntry]:
    awarding_id = generate_uuid7()
    occurred_at = datetime.utcnow()

    awarding = _build_awarding(awarding_id, badge, awardee, occurred_at)
    event = _build_awarding_event(occurred_at, badge, awardee, initiator)
    log_entry = _build_awarding_log_entry(
        occurred_at, badge, awardee, initiator
    )

    return awarding, event, log_entry


def _build_awarding(
    awarding_id: UUID, badge: Badge, awardee: User, awarded_at: datetime
) -> BadgeAwarding:
    return BadgeAwarding(
        id=awarding_id,
        badge_id=badge.id,
        awardee_id=awardee.id,
        awarded_at=awarded_at,
    )


def _build_awarding_event(
    occurred_at: datetime, badge: Badge, awardee: User, initiator: User | None
) -> UserBadgeAwardedEvent:
    return UserBadgeAwardedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        badge_id=badge.id,
        badge_label=badge.label,
        awardee_id=awardee.id,
        awardee_screen_name=awardee.screen_name,
    )


def _build_awarding_log_entry(
    occurred_at: datetime, badge: Badge, awardee: User, initiator: User | None
) -> UserLogEntry:
    data = {'badge_id': str(badge.id)}
    if initiator:
        data['initiator_id'] = str(initiator.id)

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-badge-awarded',
        user_id=awardee.id,
        data=data,
    )
