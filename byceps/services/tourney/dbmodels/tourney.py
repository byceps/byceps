"""
byceps.services.tourney.dbmodels.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.database import db, generate_uuid7
from byceps.services.tourney.models import TourneyCategoryID
from byceps.typing import PartyID
from byceps.util.instances import ReprBuilder

from .tourney_category import DbTourneyCategory


class DbTourney(db.Model):
    """A tournament."""

    __tablename__ = 'tourneys'
    __table_args__ = (
        db.UniqueConstraint('category_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False
    )
    title = db.Column(db.UnicodeText, nullable=False)
    subtitle = db.Column(db.UnicodeText, nullable=True)
    logo_url = db.Column(db.UnicodeText, nullable=True)
    category_id = db.Column(
        db.Uuid,
        db.ForeignKey('tourney_categories.id'),
        index=True,
        nullable=False,
    )
    category = db.relationship(DbTourneyCategory)
    max_participant_count = db.Column(db.Integer, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        party_id: PartyID,
        title: str,
        category_id: TourneyCategoryID,
        max_participant_count: int,
        starts_at: datetime,
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

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('party_id')
            .add_with_lookup('title')
            .build()
        )
