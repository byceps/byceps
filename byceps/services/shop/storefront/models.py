"""
byceps.services.shop.storefront.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....util.instances import ReprBuilder

from ..sequence.transfer.models import NumberSequenceID
from ..shop.transfer.models import ShopID

from .transfer.models import StorefrontID


class Storefront(db.Model):
    """A storefront.

    The entrypoint from a site to a shop.
    """

    __tablename__ = 'shop_storefronts'

    id = db.Column(db.UnicodeText, primary_key=True)
    shop_id = db.Column(db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False)
    order_number_sequence_id = db.Column(db.Uuid, db.ForeignKey('shop_sequences.id'), nullable=False)
    closed = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        storefront_id: StorefrontID,
        shop_id: ShopID,
        order_number_sequence_id: NumberSequenceID,
        closed: bool,
    ) -> None:
        self.id = storefront_id
        self.shop_id = shop_id
        self.order_number_sequence_id = order_number_sequence_id
        self.closed = closed

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('shop_id') \
            .build()
