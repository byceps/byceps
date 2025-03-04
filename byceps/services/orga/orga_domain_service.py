"""
byceps.services.orga.orga_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.brand.models import Brand
from byceps.services.core.events import EventBrand, EventUser
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .events import (
    OrgaStatusGrantedEvent,
    OrgaStatusRevokedEvent,
)


def grant_orga_status(
    user: User, brand: Brand, initiator: User
) -> tuple[OrgaStatusGrantedEvent, UserLogEntry]:
    """Grant organizer status to the user for the brand."""
    occurred_at = datetime.utcnow()

    event = _build_orga_status_granted_event(
        occurred_at, user, brand, initiator
    )
    log_entry = _build_orga_status_granted_log_entry(
        occurred_at, user, brand, initiator
    )

    return event, log_entry


def _build_orga_status_granted_event(
    occurred_at: datetime, user: User, brand: Brand, initiator: User
) -> OrgaStatusGrantedEvent:
    return OrgaStatusGrantedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        user=EventUser.from_user(user),
        brand=EventBrand.from_brand(brand),
    )


def _build_orga_status_granted_log_entry(
    occurred_at: datetime, user: User, brand: Brand, initiator: User
) -> UserLogEntry:
    data = {
        'brand_id': str(brand.id),
        'initiator_id': str(initiator.id),
    }

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='orgaflag-added',
        user_id=user.id,
        initiator_id=initiator.id,
        data=data,
    )


def revoke_orga_status(
    user: User, brand: Brand, initiator: User
) -> tuple[OrgaStatusRevokedEvent, UserLogEntry]:
    """Revoke the user's organizer status for the brand."""
    occurred_at = datetime.utcnow()

    event = _build_orga_status_revoked_event(
        occurred_at, user, brand, initiator
    )
    log_entry = _build_orga_status_revoked_log_entry(
        occurred_at, user, brand, initiator
    )

    return event, log_entry


def _build_orga_status_revoked_event(
    occurred_at: datetime, user: User, brand: Brand, initiator: User
) -> OrgaStatusRevokedEvent:
    return OrgaStatusRevokedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        user=EventUser.from_user(user),
        brand=EventBrand.from_brand(brand),
    )


def _build_orga_status_revoked_log_entry(
    occurred_at: datetime, user: User, brand: Brand, initiator: User
) -> UserLogEntry:
    data = {
        'brand_id': str(brand.id),
        'initiator_id': str(initiator.id),
    }

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='orgaflag-removed',
        user_id=user.id,
        initiator_id=initiator.id,
        data=data,
    )
