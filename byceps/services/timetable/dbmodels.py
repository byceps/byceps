"""
byceps.services.timetable.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.party.models import PartyID

from .models import TimetableID, TimetableItemID


class DbTimetable(db.Model):
    """An timetable for a party."""

    __tablename__ = 'timetables'

    id: Mapped[TimetableID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), unique=True
    )
    hidden: Mapped[bool]

    def __init__(
        self,
        timetable_id: TimetableID,
        party_id: PartyID,
        hidden: bool,
    ) -> None:
        self.id = timetable_id
        self.party_id = party_id
        self.hidden = hidden


class DbTimetableItem(db.Model):
    """An item on a timetable."""

    __tablename__ = 'timetable_items'

    id: Mapped[TimetableItemID] = mapped_column(db.Uuid, primary_key=True)
    timetable_id: Mapped[TimetableID] = mapped_column(
        db.Uuid, db.ForeignKey('timetables.id'), index=True
    )
    scheduled_at: Mapped[datetime]
    description: Mapped[str] = mapped_column(db.UnicodeText)
    location: Mapped[str | None] = mapped_column(db.UnicodeText)
    hidden: Mapped[bool]

    def __init__(
        self,
        item_id: TimetableItemID,
        timetable_id: TimetableID,
        scheduled_at: datetime,
        description: str,
        location: str | None,
        hidden: bool,
    ) -> None:
        self.id = item_id
        self.timetable_id = timetable_id
        self.scheduled_at = scheduled_at
        self.description = description
        self.location = location
        self.hidden = hidden
