"""
byceps.services.timetable.timetable_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import date, datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import Party, PartyID
from byceps.services.user.models.user import User

from . import timetable_domain_service
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


def create_timetable(
    party: Party,
    hidden: bool,
) -> Timetable:
    """Create a timetable."""
    timetable = timetable_domain_service.create_timetable(party.id, hidden)

    db_timetable = DbTimetable(
        timetable.id,
        timetable.party_id,
        timetable.hidden,
    )
    db.session.add(db_timetable)
    db.session.commit()

    return timetable


def find_timetable(timetable_id: TimetableID) -> Timetable | None:
    """Return the timetable."""
    db_timetable = db.session.get(DbTimetable, timetable_id)

    if db_timetable is None:
        return None

    items = _get_items(db_timetable.id)

    return _db_entity_to_timetable(db_timetable, items)


def find_timetable_for_party(party_id: PartyID) -> Timetable | None:
    """Return the timetable for the party."""
    db_timetable = db.session.scalars(
        select(DbTimetable).filter_by(party_id=party_id)
    ).one_or_none()

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
    db_items = db.session.scalars(
        select(DbTimetableItem).filter_by(timetable_id=timetable_id)
    ).all()

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

    db_item = DbTimetableItem(
        item.id,
        item.timetable_id,
        item.scheduled_at,
        item.description,
        item.location,
        item.link_target,
        item.link_label,
        item.hidden,
    )
    db.session.add(db_item)
    db.session.commit()

    return item


def update_item(
    item_id: TimetableItemID,
    scheduled_at: datetime,
    description: str,
    location: str | None,
    link_target: str | None,
    link_label: str | None,
    hidden: bool,
) -> TimetableItem:
    """Update a timetable item."""
    db_item = db.session.get(DbTimetableItem, item_id)
    if db_item is None:
        raise ValueError(f'Unknown item ID "{item_id}"')

    db_item.scheduled_at = scheduled_at
    db_item.description = description
    db_item.location = location
    db_item.link_target = link_target
    db_item.link_label = link_label
    db_item.hidden = hidden

    db.session.commit()

    return _db_entity_to_item(db_item)


def delete_item(item_id: TimetableItemID, initiator: User) -> None:
    """Delete a timetable item."""
    db.session.execute(
        delete(DbTimetableItem).where(DbTimetableItem.id == item_id)
    )

    db.session.commit()


def find_item(item_id: TimetableItemID) -> TimetableItem | None:
    """Return the timetable item."""
    db_item = db.session.get(DbTimetableItem, item_id)

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
