"""
byceps.services.shop.sequence.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db
from ....util.instances import ReprBuilder

from ..shop.transfer.models import ShopID

from .transfer.models import Purpose


class NumberSequence(db.Model):
    """A shop-specific integer sequence for a purpose."""

    __tablename__ = 'shop_sequences'

    shop_id = db.Column(db.UnicodeText, db.ForeignKey('shops.id'), primary_key=True)
    _purpose = db.Column('purpose', db.UnicodeText, primary_key=True)
    prefix = db.Column(db.UnicodeText, unique=True, nullable=False)
    value = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, shop_id: ShopID, purpose: Purpose, prefix: str) -> None:
        self.shop_id = shop_id
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
            .add('shop', self.shop_id) \
            .add('purpose', self.purpose.name) \
            .add_with_lookup('prefix') \
            .add_with_lookup('value') \
            .build()
