# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.models.category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...party.models import Party


class CategoryQuery(BaseQuery):

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


class Category(db.Model):
    """A seat's category which may (indirectly) indicate its price and
    features.
    """
    __tablename__ = 'seat_categories'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )
    query_class = CategoryQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party, backref='seat_categories')
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
