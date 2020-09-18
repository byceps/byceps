"""
byceps.services.tourney.models.tourney_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.ext.orderinglist import ordering_list

from ....database import db, generate_uuid
from ....typing import PartyID
from ....util.instances import ReprBuilder

from ...party.models.party import Party


class TourneyCategory(db.Model):
    """One of potentially multiple tourney categories for a party."""

    __tablename__ = 'tourney_categories'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party,
                            backref=db.backref('tourney_categories',
                                               order_by='TourneyCategory.position',
                                               collection_class=ordering_list('position', count_from=1)))
    position = db.Column(db.Integer, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, party_id: PartyID, title: str) -> None:
        self.party_id = party_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party_id') \
            .add_with_lookup('title') \
            .build()
