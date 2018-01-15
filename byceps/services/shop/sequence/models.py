"""
byceps.services.shop.sequence.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder


Purpose = Enum('Purpose', ['article', 'order'])


class PartySequence(db.Model):
    """A sequence for a party and a purpose."""
    __tablename__ = 'shop_party_sequences'

    party_id = db.Column(db.Unicode(40), db.ForeignKey('parties.id'), primary_key=True)
    _purpose = db.Column('purpose', db.Unicode(20), primary_key=True)
    prefix = db.Column(db.Unicode(20), unique=True, nullable=False)
    value = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, party_id: PartyID, purpose: Purpose, prefix: str
                ) -> None:
        self.party_id = party_id
        self.purpose = purpose
        self.prefix = prefix

    @hybrid_property
    def purpose(self) -> Purpose:
        return Purpose[self._purpose]

    @purpose.setter
    def purpose(self, purpose: Purpose) -> None:
        assert purpose is not None
        self._purpose = purpose.name

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('party', self.party_id) \
            .add('purpose', self.purpose.name) \
            .add_with_lookup('prefix') \
            .add_with_lookup('value') \
            .build()
