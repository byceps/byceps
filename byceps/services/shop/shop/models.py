"""
byceps.services.shop.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder


ShopID = NewType('ShopID', str)


class Shop(db.Model):
    """A shop."""
    __tablename__ = 'shops'

    id = db.Column(db.Unicode(40), primary_key=True)
    party_id = db.Column(db.Unicode(40), db.ForeignKey('parties.id'), index=True, nullable=False)

    def __init__(self, shop_id: ShopID, party_id: PartyID) -> None:
        self.id = shop_id
        self.party_id = party_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .build()
