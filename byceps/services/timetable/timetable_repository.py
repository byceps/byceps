"""
byceps.services.timetable.timetable_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import PartyID

from .dbmodels import DbTimetable, DbTimetableItem
from .models import Timetable, TimetableID, TimetableItem, TimetableItemID


# -------------------------------------------------------------------- #
# timetable


def create_timetable(timetable: Timetable) -> None:
    """Create a timetable."""
    db_timetable = DbTimetable(
        timetable.id,
        timetable.party_id,
        timetable.hidden,
    )
    db.session.add(db_timetable)
    db.session.commit()


def find_timetable(timetable_id: TimetableID) -> DbTimetable | None:
    """Return the timetable."""
    return db.session.get(DbTimetable, timetable_id)


def find_timetable_for_party(party_id: PartyID) -> DbTimetable | None:
    """Return the timetable for the party."""
    return db.session.scalars(
        select(DbTimetable).filter_by(party_id=party_id)
    ).one_or_none()


# -------------------------------------------------------------------- #
# item


def create_item(item: TimetableItem) -> None:
    """Create a timetable item."""
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


def update_item(item: TimetableItem) -> None:
    """Update a timetable item."""
    db_item = db.session.get(DbTimetableItem, item.id)
    if db_item is None:
        raise ValueError(f'Unknown item ID "{item.id}"')

    db_item.scheduled_at = item.scheduled_at
    db_item.description = item.description
    db_item.location = item.location
    db_item.link_target = item.link_target
    db_item.link_label = item.link_label
    db_item.hidden = item.hidden

    db.session.commit()


def delete_item(item_id: TimetableItemID) -> None:
    """Delete a timetable item."""
    db.session.execute(
        delete(DbTimetableItem).where(DbTimetableItem.id == item_id)
    )

    db.session.commit()


def find_item(item_id: TimetableItemID) -> DbTimetableItem | None:
    """Return the timetable item."""
    return db.session.get(DbTimetableItem, item_id)


def get_items(timetable_id: TimetableID) -> Sequence[DbTimetableItem]:
    return db.session.scalars(
        select(DbTimetableItem).filter_by(timetable_id=timetable_id)
    ).all()
