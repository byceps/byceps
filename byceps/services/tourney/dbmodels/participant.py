"""
byceps.services.tourney.dbmodels.participant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.tourney.models import ParticipantID, TourneyID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .tourney import DbTourney


class DbParticipant(db.Model):
    """One or more players participating in a tourney as a single unit."""

    __tablename__ = 'tourney_participants'

    id: Mapped[ParticipantID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    tourney_id: Mapped[TourneyID] = mapped_column(
        db.Uuid, db.ForeignKey('tourneys.id'), index=True
    )
    tourney: Mapped[DbTourney] = relationship(DbTourney)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_by_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    created_by: Mapped[DbUser] = relationship(DbUser)
    title: Mapped[str] = mapped_column(db.UnicodeText)
    max_size: Mapped[Optional[int]]  # noqa: UP007

    def __init__(
        self, tourney_id: TourneyID, title: str, max_size: int
    ) -> None:
        self.tourney_id = tourney_id
        self.title = title
        self.max_size = max_size

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('tourney')
            .add_with_lookup('title')
            .add_with_lookup('max_size')
            .build()
        )
