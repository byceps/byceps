"""
byceps.services.user.log.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder

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
    initiator_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
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

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_custom(repr(self.event_type))
            .add_with_lookup('user_id')
            .add_with_lookup('data')
            .build()
        )
