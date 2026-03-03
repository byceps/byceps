"""
byceps.services.timetable.timetable_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from byceps.services.party.models import PartyID
from byceps.util.uuid import generate_uuid7

from .models import Timetable, TimetableID, TimetableItem, TimetableItemID


def create_timetable(
    party_id: PartyID,
    hidden: bool,
) -> Timetable:
    """Create a timetable."""
    timetable_id = TimetableID(generate_uuid7())

    return Timetable(
        id=timetable_id,
        party_id=party_id,
        hidden=hidden,
        items=[],
    )


def create_item(
    timetable_id: TimetableID,
    scheduled_at: datetime,
    description: str,
    location: str | None,
    link_target: str | None,
    link_label: str | None,
    hidden: bool,
) -> TimetableItem:
    """Create a timetable item."""
    item_id = TimetableItemID(generate_uuid7())

    return TimetableItem(
        id=item_id,
        timetable_id=timetable_id,
        scheduled_at=scheduled_at,
        description=description,
        location=location,
        link_target=link_target,
        link_label=link_label,
        hidden=hidden,
    )


def update_item(
    item: TimetableItem,
    scheduled_at: datetime,
    description: str,
    location: str | None,
    link_target: str | None,
    link_label: str | None,
    hidden: bool,
) -> TimetableItem:
    """Update a timetable item."""
    return dataclasses.replace(
        item,
        scheduled_at=scheduled_at,
        description=description,
        location=location,
        link_target=link_target,
        link_label=link_label,
        hidden=hidden,
    )
