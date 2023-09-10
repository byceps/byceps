"""
byceps.services.orga.orga_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.database import generate_uuid7
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.typing import BrandID


def grant_orga_status(
    user: User, brand_id: BrandID, initiator: User
) -> UserLogEntry:
    """Grant organizer status to the user for the brand."""
    occurred_at = datetime.utcnow()

    log_entry = _build_orga_status_granted_log_entry(
        occurred_at, user, brand_id, initiator
    )

    return log_entry


def _build_orga_status_granted_log_entry(
    occurred_at: datetime, user: User, brand_id: BrandID, initiator: User
) -> UserLogEntry:
    data = {
        'brand_id': str(brand_id),
        'initiator_id': str(initiator.id),
    }

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='orgaflag-added',
        user_id=user.id,
        data=data,
    )


def revoke_orga_status(
    user: User, brand_id: BrandID, initiator: User
) -> UserLogEntry:
    """Revoke the user's organizer status for the brand."""
    occurred_at = datetime.utcnow()

    log_entry = _build_orga_status_revoked_log_entry(
        occurred_at, user, brand_id, initiator
    )

    return log_entry


def _build_orga_status_revoked_log_entry(
    occurred_at: datetime, user: User, brand_id: BrandID, initiator: User
) -> UserLogEntry:
    data = {
        'brand_id': str(brand_id),
        'initiator_id': str(initiator.id),
    }

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='orgaflag-removed',
        user_id=user.id,
        data=data,
    )
