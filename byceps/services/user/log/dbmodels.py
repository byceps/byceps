"""
byceps.services.user.log.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID

from .models import UserLogEntryData


class DbUserLogEntry(db.Model):
    """A log entry regarding a user."""

    __tablename__ = 'user_log_entries'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    occurred_at: Mapped[datetime]
    event_type: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    user: Mapped[DbUser] = relationship(DbUser, foreign_keys=[user_id])
    initiator_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    initiator: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[initiator_id]
    )
    data: Mapped[UserLogEntryData] = mapped_column(db.JSONB)

    def __init__(
        self,
        entry_id: UUID,
        occurred_at: datetime,
        event_type: str,
        user_id: UserID,
        initiator_id: UserID | None,
        data: UserLogEntryData,
    ) -> None:
        self.id = entry_id
        self.occurred_at = occurred_at
        self.event_type = event_type
        self.user_id = user_id
        self.initiator_id = initiator_id
        self.data = data
