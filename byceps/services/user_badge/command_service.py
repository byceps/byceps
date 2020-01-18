"""
byceps.services.user_badge.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional, Tuple

from ...database import db
from ...events.user_badge import UserBadgeAwarded
from ...typing import BrandID, UserID

from ..user import event_service
from .models.awarding import BadgeAwarding as DbBadgeAwarding
from .models.badge import Badge as DbBadge
from .service import _db_entity_to_badge
from .transfer.models import Badge, BadgeAwarding, BadgeID


def create_badge(
    slug: str,
    label: str,
    image_filename: str,
    *,
    brand_id: Optional[BrandID] = None,
    description: Optional[str] = None,
    featured: bool = False,
) -> Badge:
    """Introduce a new badge."""
    badge = DbBadge(
        slug,
        label,
        image_filename,
        brand_id=brand_id,
        description=description,
        featured=featured,
    )

    db.session.add(badge)
    db.session.commit()

    return _db_entity_to_badge(badge)


def award_badge_to_user(
    badge_id: BadgeID, user_id: UserID, *, initiator_id: Optional[UserID] = None
) -> Tuple[BadgeAwarding, UserBadgeAwarded]:
    """Award the badge to the user."""
    awarded_at = datetime.utcnow()

    awarding = DbBadgeAwarding(badge_id, user_id, awarded_at=awarded_at)
    db.session.add(awarding)

    event_data = {'badge_id': str(badge_id)}
    if initiator_id:
        event_data['initiator_id'] = str(initiator_id)
    event = event_service.build_event(
        'user-badge-awarded', user_id, event_data, occurred_at=awarded_at
    )
    db.session.add(event)

    db.session.commit()

    awarding_dto = _db_entity_to_badge_awarding(awarding)

    event = UserBadgeAwarded(
        occurred_at=awarded_at,
        user_id=user_id,
        badge_id=badge_id,
        initiator_id=initiator_id,
    )

    return awarding_dto, event


def _db_entity_to_badge_awarding(entity: DbBadgeAwarding) -> BadgeAwarding:
    return BadgeAwarding(
        entity.id,
        entity.badge_id,
        entity.user_id,
        entity.awarded_at
    )
