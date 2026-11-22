"""
byceps.services.timetable.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import UnicodeText, Uuid

from byceps.database import db
from byceps.services.party.models import PartyID

from .models import TimetableID, TimetableItemID


class DbTimetable(db.Model):
    """An timetable for a party."""

    __tablename__ = 'timetables'

    id: Mapped[TimetableID] = mapped_column(Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        UnicodeText, ForeignKey('parties.id'), unique=True
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

    id: Mapped[TimetableItemID] = mapped_column(Uuid, primary_key=True)
    timetable_id: Mapped[TimetableID] = mapped_column(
        Uuid, ForeignKey('timetables.id'), index=True
    )
    scheduled_at: Mapped[datetime]
    description: Mapped[str] = mapped_column(UnicodeText)
    location: Mapped[str | None] = mapped_column(UnicodeText)
    link_target: Mapped[str | None] = mapped_column(UnicodeText)
    link_label: Mapped[str | None] = mapped_column(UnicodeText)
    hidden: Mapped[bool]

    def __init__(
        self,
        item_id: TimetableItemID,
        timetable_id: TimetableID,
        scheduled_at: datetime,
        description: str,
        location: str | None,
        link_target: str | None,
        link_label: str | None,
        hidden: bool,
    ) -> None:
        self.id = item_id
        self.timetable_id = timetable_id
        self.scheduled_at = scheduled_at
        self.description = description
        self.location = location
        self.link_target = link_target
        self.link_label = link_label
        self.hidden = hidden
