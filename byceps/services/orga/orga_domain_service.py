"""
byceps.services.orga.orga_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.brand.models import Brand
from byceps.services.core.events import EventBrand
from byceps.services.user.log import user_log_domain_service
from byceps.services.user.log.models import UserLogEntry
from byceps.services.user.models.user import User

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

    log_entry = _build_orga_status_granted_log_entry(event)

    return event, log_entry


def _build_orga_status_granted_event(
    occurred_at: datetime, user: User, brand: Brand, initiator: User
) -> OrgaStatusGrantedEvent:
    return OrgaStatusGrantedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        brand=EventBrand.from_brand(brand),
    )


def _build_orga_status_granted_log_entry(
    event: OrgaStatusGrantedEvent,
) -> UserLogEntry:
    data = {'brand_id': str(event.brand.id)}

    return user_log_domain_service.build_entry(
        'orgaflag-added',
        event.user,
        data,
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )


def revoke_orga_status(
    user: User, brand: Brand, initiator: User
) -> tuple[OrgaStatusRevokedEvent, UserLogEntry]:
    """Revoke the user's organizer status for the brand."""
    occurred_at = datetime.utcnow()

    event = _build_orga_status_revoked_event(
        occurred_at, user, brand, initiator
    )

    log_entry = _build_orga_status_revoked_log_entry(event)

    return event, log_entry


def _build_orga_status_revoked_event(
    occurred_at: datetime, user: User, brand: Brand, initiator: User
) -> OrgaStatusRevokedEvent:
    return OrgaStatusRevokedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        brand=EventBrand.from_brand(brand),
    )


def _build_orga_status_revoked_log_entry(
    event: OrgaStatusRevokedEvent,
) -> UserLogEntry:
    data = {'brand_id': str(event.brand.id)}

    return user_log_domain_service.build_entry(
        'orgaflag-removed',
        event.user,
        data,
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )
