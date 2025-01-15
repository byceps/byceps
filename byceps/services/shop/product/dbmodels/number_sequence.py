"""
byceps.services.shop.product.dbmodels.sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.shop.product.models import ProductNumberSequenceID
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder


class DbProductNumberSequence(db.Model):
    """A shop-specific, unique product number sequence."""

    __tablename__ = 'shop_product_number_sequences'

    id: Mapped[ProductNumberSequenceID] = mapped_column(
        db.Uuid, primary_key=True
    )
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    prefix: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    value: Mapped[int]
    archived: Mapped[bool]

    def __init__(
        self,
        sequence_id: ProductNumberSequenceID,
        shop_id: ShopID,
        prefix: str,
        value: int,
        *,
        archived: bool = False,
    ) -> None:
        self.id = sequence_id
        self.shop_id = shop_id
        self.prefix = prefix
        self.value = value
        self.archived = archived

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('prefix')
            .add_with_lookup('value')
            .build()
        )
