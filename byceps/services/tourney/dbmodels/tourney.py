"""
byceps.services.tourney.dbmodels.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.tourney.models import TourneyCategoryID, TourneyID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .tourney_category import DbTourneyCategory


class DbTourney(db.Model):
    """A tournament."""

    __tablename__ = 'tourneys'
    __table_args__ = (db.UniqueConstraint('category_id', 'title'),)

    id: Mapped[TourneyID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    title: Mapped[str] = mapped_column(db.UnicodeText)
    subtitle: Mapped[str | None] = mapped_column(db.UnicodeText)
    logo_url: Mapped[str | None] = mapped_column(db.UnicodeText)
    category_id: Mapped[TourneyCategoryID] = mapped_column(
        db.Uuid,
        db.ForeignKey('tourney_categories.id'),
        index=True,
        nullable=False,
    )
    category: Mapped[DbTourneyCategory] = relationship(DbTourneyCategory)
    max_participant_count: Mapped[int]
    starts_at: Mapped[datetime]
    registration_open: Mapped[bool]

    def __init__(
        self,
        party_id: PartyID,
        title: str,
        category_id: TourneyCategoryID,
        max_participant_count: int,
        starts_at: datetime,
        registration_open: bool,
        *,
        subtitle: str | None = None,
        logo_url: str | None = None,
    ) -> None:
        self.party_id = party_id
        self.title = title
        self.subtitle = subtitle
        self.logo_url = logo_url
        self.category_id = category_id
        self.max_participant_count = max_participant_count
        self.starts_at = starts_at
        self.registration_open = registration_open

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('party_id')
            .add_with_lookup('title')
            .build()
        )
