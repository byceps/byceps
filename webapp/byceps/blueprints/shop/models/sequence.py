# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.models.sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db
from ....util.instances import ReprBuilder

from ...party.models import Party


PartySequencePurpose = Enum('PartySequencePurpose', ['article', 'order'])


class PartySequence(db.Model):
    """A sequence for a party and a purpose."""
    __tablename__ = 'shop_party_sequences'

    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), primary_key=True)
    party = db.relationship(Party)
    _purpose = db.Column('purpose', db.Unicode(20), primary_key=True)
    value = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, party, purpose):
        self.party = party
        self.purpose = purpose

    @hybrid_property
    def purpose(self):
        return PartySequencePurpose[self._purpose]

    @purpose.setter
    def purpose(self, purpose):
        assert purpose is not None
        self._purpose = purpose.name

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add('purpose', self.purpose.name) \
            .add_with_lookup('value') \
            .build()
