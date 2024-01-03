"""
byceps.services.shop.order.dbmodels.number_sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.shop.order.models.number import OrderNumberSequenceID
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4


class DbOrderNumberSequence(db.Model):
    """A shop-specific, unique order number sequence."""

    __tablename__ = 'shop_order_number_sequences'

    id: Mapped[OrderNumberSequenceID] = mapped_column(
        db.Uuid, default=generate_uuid4, primary_key=True
    )
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    prefix: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    value: Mapped[int] = mapped_column(default=0)

    def __init__(
        self,
        shop_id: ShopID,
        prefix: str,
        *,
        value: int | None = 0,
    ) -> None:
        if value is None:
            value = 0

        self.shop_id = shop_id
        self.prefix = prefix
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('prefix')
            .add_with_lookup('value')
            .build()
        )
