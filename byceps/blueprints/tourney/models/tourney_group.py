# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney.models.tourney_group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...party.models import Party


class TourneyGroupQuery(BaseQuery):

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


class TourneyGroup(db.Model):
    """One of potentially multiple tourney groups for a party."""
    __tablename__ = 'tourney_groups'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )
    query_class = TourneyGroupQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    position = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)

    def __init__(self, party, position, title):
        self.party = party
        self.position = position
        self.title = title

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party') \
            .add_with_lookup('title') \
            .build()
