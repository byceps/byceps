"""
byceps.services.timetable.timetable_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import date, datetime

from byceps.services.party.models import Party, PartyID
from byceps.util.result import Err, Ok, Result

from . import timetable_domain_service, timetable_repository
from .dbmodels import DbTimetable, DbTimetableItem
from .models import (
    Timetable,
    TimetableGroupedByDay,
    TimetableID,
    TimetableItem,
    TimetableItemID,
)


# -------------------------------------------------------------------- #
# timetable


def copy_timetable(
    source_party_id: PartyID,
    target_party_id: PartyID,
) -> Result[None, str]:
    """Copy items from one timetable to another."""
    source_timetable = find_timetable_for_party(source_party_id)
    if source_timetable is None:
        return Err(f'Source timetable not found for party "{source_party_id}"')

    target_timetable = find_timetable_for_party(target_party_id)
    if target_timetable is None:
        return Err(f'Target timetable not found for party "{target_party_id}"')

    for source_item in source_timetable.items:
        create_item(
            target_timetable.id,
            source_item.scheduled_at,
            source_item.description,
            source_item.location,
            source_item.link_target,
            source_item.link_label,
            source_item.hidden,
        )

    return Ok(None)


def create_timetable(
    party: Party,
    hidden: bool,
) -> Timetable:
    """Create a timetable."""
    timetable = timetable_domain_service.create_timetable(party.id, hidden)

    timetable_repository.create_timetable(timetable)

    return timetable


def find_timetable(timetable_id: TimetableID) -> Timetable | None:
    """Return the timetable."""
    db_timetable = timetable_repository.find_timetable(timetable_id)

    if db_timetable is None:
        return None

    items = _get_items(db_timetable.id)

    return _db_entity_to_timetable(db_timetable, items)


def find_timetable_for_party(party_id: PartyID) -> Timetable | None:
    """Return the timetable for the party."""
    db_timetable = timetable_repository.find_timetable_for_party(party_id)

    if db_timetable is None:
        return None

    items = _get_items(db_timetable.id)

    return _db_entity_to_timetable(db_timetable, items)


def find_timetable_grouped_by_day_for_party(
    party_id: PartyID, *, include_hidden_items: bool
) -> TimetableGroupedByDay | None:
    """Return the timetable, items grouped by day, for the party."""
    timetable = find_timetable_for_party(party_id)

    if timetable is None:
        return None

    return group_timetable_items_by_day(
        timetable, include_hidden_items=include_hidden_items
    )


def _get_items(timetable_id: TimetableID) -> list[TimetableItem]:
    db_items = timetable_repository.get_items(timetable_id)

    items = [_db_entity_to_item(db_item) for db_item in db_items]
    items.sort(key=lambda item: (item.scheduled_at, item.description))

    return items


def _db_entity_to_timetable(
    db_timetable: DbTimetable, items: list[TimetableItem]
) -> Timetable:
    return Timetable(
        id=db_timetable.id,
        party_id=db_timetable.party_id,
        hidden=db_timetable.hidden,
        items=items,
    )


def group_timetable_items_by_day(
    timetable: Timetable, *, include_hidden_items: bool
) -> TimetableGroupedByDay:
    items_by_day = _group_items_by_day(
        timetable, include_hidden_items=include_hidden_items
    )

    days_and_items = []
    for day, day_items in items_by_day.items():
        day_items.sort(key=lambda item: item.scheduled_at)
        days_and_items.append((day, day_items))
    days_and_items.sort(key=lambda day_and_items: day_and_items[0])

    return TimetableGroupedByDay(
        id=timetable.id,
        party_id=timetable.party_id,
        hidden=timetable.hidden,
        items=days_and_items,
    )


def _group_items_by_day(
    timetable: Timetable, *, include_hidden_items: bool
) -> dict[date, list[TimetableItem]]:
    items_by_day = defaultdict(list)

    for item in timetable.items:
        if not item.hidden or include_hidden_items:
            items_by_day[item.scheduled_at.date()].append(item)

    return dict(items_by_day)


# -------------------------------------------------------------------- #
# item


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
    item = timetable_domain_service.create_item(
        timetable_id,
        scheduled_at,
        description,
        location,
        link_target,
        link_label,
        hidden,
    )

    timetable_repository.create_item(item)

    return item


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
    updated_item = timetable_domain_service.update_item(
        item,
        scheduled_at,
        description,
        location,
        link_target,
        link_label,
        hidden,
    )

    timetable_repository.update_item(updated_item)

    return updated_item


def delete_item(item_id: TimetableItemID) -> None:
    """Delete a timetable item."""
    timetable_repository.delete_item(item_id)


def find_item(item_id: TimetableItemID) -> TimetableItem | None:
    """Return the timetable item."""
    db_item = timetable_repository.find_item(item_id)

    if db_item is None:
        return None

    return _db_entity_to_item(db_item)


def _db_entity_to_item(db_item: DbTimetableItem) -> TimetableItem:
    return TimetableItem(
        id=db_item.id,
        timetable_id=db_item.timetable_id,
        scheduled_at=db_item.scheduled_at,
        description=db_item.description,
        location=db_item.location,
        link_target=db_item.link_target,
        link_label=db_item.link_label,
        hidden=db_item.hidden,
    )
