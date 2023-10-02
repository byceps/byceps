"""
byceps.services.tourney.dbmodels.tourney_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.dbmodels import DbParty
from byceps.services.tourney.models import TourneyCategoryID
from byceps.typing import PartyID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4


class DbTourneyCategory(db.Model):
    """One of potentially multiple tourney categories for a party."""

    __tablename__ = 'tourney_categories'
    __table_args__ = (db.UniqueConstraint('party_id', 'title'),)

    id: Mapped[TourneyCategoryID] = mapped_column(
        db.Uuid, default=generate_uuid4, primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    party: Mapped[DbParty] = relationship(
        DbParty,
        backref=db.backref(
            'tourney_categories',
            order_by='DbTourneyCategory.position',
            collection_class=ordering_list('position', count_from=1),
        ),
    )
    position: Mapped[int]
    title: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, party_id: PartyID, title: str) -> None:
        self.party_id = party_id
        self.title = title

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('party_id')
            .add_with_lookup('title')
            .build()
        )
