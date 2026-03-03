"""
byceps.services.whereabouts.whereabouts_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.services.core.events import EventParty
from byceps.services.party.models import Party
from byceps.services.user.models import User
from byceps.util.uuid import generate_uuid7

from .events import WhereaboutsStatusUpdatedEvent
from .models import (
    IPAddress,
    Whereabouts,
    WhereaboutsID,
    WhereaboutsStatus,
    WhereaboutsUpdate,
)


def create_whereabouts(
    party: Party,
    name: str,
    description: str,
    position: int,
    *,
    hidden_if_empty: bool = False,
    secret: bool = False,
) -> Whereabouts:
    """Create whereabouts."""
    whereabouts_id = WhereaboutsID(generate_uuid7())

    return Whereabouts(
        id=whereabouts_id,
        party=party,
        name=name,
        description=description,
        position=position,
        hidden_if_empty=hidden_if_empty,
        secret=secret,
    )


def set_status(
    user: User,
    whereabouts: Whereabouts,
    *,
    source_address: IPAddress | None = None,
) -> tuple[WhereaboutsStatus, WhereaboutsUpdate, WhereaboutsStatusUpdatedEvent]:
    """Set a user's whereabouts."""
    update_id = generate_uuid7()
    set_at = datetime.utcnow()

    status = WhereaboutsStatus(
        user=user,
        whereabouts_id=whereabouts.id,
        set_at=set_at,
    )

    update = WhereaboutsUpdate(
        id=update_id,
        user=user,
        whereabouts_id=whereabouts.id,
        created_at=set_at,
        source_address=source_address,
    )

    event = WhereaboutsStatusUpdatedEvent(
        occurred_at=set_at,
        initiator=user,
        party=EventParty.from_party(whereabouts.party),
        user=user,
        whereabouts_description=whereabouts.description,
    )

    return status, update, event
