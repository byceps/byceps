# -*- coding: utf-8 -*-

"""
byceps.services.tourney.models.tourney_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.ext.orderinglist import ordering_list

from ....database import db, generate_uuid
from ....services.party.models import Party
from ....util.instances import ReprBuilder


class TourneyCategory(db.Model):
    """One of potentially multiple tourney categories for a party."""
    __tablename__ = 'tourney_categories'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party,
                            backref=db.backref('tourney_categories',
                                               order_by='TourneyCategory.position',
                                               collection_class=ordering_list('position', count_from=1)))
    position = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)

    def __init__(self, party, title):
        self.party = party
        self.title = title

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party') \
            .add_with_lookup('title') \
            .build()
