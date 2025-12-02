"""
byceps.services.user_badge.user_badge_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from byceps.services.user.log import user_log_domain_service
from byceps.services.user.log.models import UserLogEntry
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .errors import BadgeAwardingFailedError
from .events import UserBadgeAwardedEvent
from .models import Badge, BadgeAwarding


def award_badge(
    badge: Badge, awardee: User, *, initiator: User | None = None
) -> Result[
    tuple[BadgeAwarding, UserBadgeAwardedEvent, UserLogEntry],
    BadgeAwardingFailedError,
]:
    if not awardee.initialized:
        return Err(
            BadgeAwardingFailedError(
                f'User account {awardee.id} is not initialized.'
            )
        )

    if awardee.deleted:
        return Err(
            BadgeAwardingFailedError(
                f'User account {awardee.id} has been deleted.'
            )
        )

    awarding_id = generate_uuid7()
    occurred_at = datetime.utcnow()

    awarding = _build_awarding(awarding_id, badge, awardee, occurred_at)
    event = _build_awarding_event(occurred_at, badge, awardee, initiator)
    log_entry = _build_awarding_log_entry(event)

    return Ok((awarding, event, log_entry))


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
        initiator=initiator,
        badge_id=badge.id,
        badge_label=badge.label,
        awardee=awardee,
    )


def _build_awarding_log_entry(event: UserBadgeAwardedEvent) -> UserLogEntry:
    data = {'badge_id': str(event.badge_id)}

    return user_log_domain_service.build_entry(
        'user-badge-awarded',
        event.awardee,
        data,
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )
