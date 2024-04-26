"""
byceps.services.timetable.timetable_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.services.party.models import Party, PartyID

from . import timetable_domain_service
from .dbmodels import DbTimetable, DbTimetableItem
from .models import Timetable, TimetableID, TimetableItem


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
