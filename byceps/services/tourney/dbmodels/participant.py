"""
byceps.services.tourney.dbmodels.participant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.tourney.models import ParticipantID, TourneyID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder

from .tourney import DbTourney


class DbParticipant(db.Model):
    """One or more players participating in a tourney as a single unit."""

    __tablename__ = 'tourney_participants'

    id: Mapped[ParticipantID] = mapped_column(db.Uuid, primary_key=True)
    tourney_id: Mapped[TourneyID] = mapped_column(
        db.Uuid, db.ForeignKey('tourneys.id'), index=True
    )
    tourney: Mapped[DbTourney] = relationship(DbTourney)
    created_at: Mapped[datetime]
    name: Mapped[str] = mapped_column(db.UnicodeText)
    manager_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    manager: Mapped[DbUser] = relationship(DbUser)

    def __init__(
        self,
        participant_id: ParticipantID,
        tourney_id: TourneyID,
        created_at: datetime,
        name: str,
        manager_id: UserID,
    ) -> None:
        self.id = participant_id
        self.tourney_id = tourney_id
        self.created_at = created_at
        self.name = name
        self.manager_id = manager_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('tourney')
            .add_with_lookup('name')
            .build()
        )
