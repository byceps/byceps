"""
byceps.services.tourney.log.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.tourney.models import TourneyID
from byceps.services.user.models.user import UserID

from .models import LogEntryData


class DbTourneyLogEntry(db.Model):
    """A log entry for a tourney."""

    __tablename__ = 'tourney_log_entries'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    occurred_at: Mapped[datetime]
    event_type: Mapped[str] = mapped_column(db.UnicodeText)
    tourney_id: Mapped[TourneyID] = mapped_column(
        db.Uuid, db.ForeignKey('tourneys.id'), index=True
    )
    initiator_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    data: Mapped[LogEntryData] = mapped_column(db.JSONB)

    def __init__(
        self,
        entry_id: UUID,
        occurred_at: datetime,
        event_type: str,
        tourney_id: TourneyID,
        initiator_id: UserID | None,
        data: LogEntryData,
    ) -> None:
        self.id = entry_id
        self.occurred_at = occurred_at
        self.event_type = event_type
        self.tourney_id = tourney_id
        self.initiator_id = initiator_id
        self.data = data
