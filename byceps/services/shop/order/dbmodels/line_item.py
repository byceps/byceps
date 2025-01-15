"""
byceps.services.shop.order.dbmodels.line_item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import (
    ProductID,
    ProductNumber,
    ProductType,
)
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import LineItemID

from .order import DbOrder


class DbLineItem(db.Model):
    """A line item that belongs to an order."""

    __tablename__ = 'shop_order_line_items'

    id: Mapped[LineItemID] = mapped_column(db.Uuid, primary_key=True)
    order_number: Mapped[OrderNumber] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_orders.order_number'),
        index=True,
    )
    order: Mapped[DbOrder] = relationship(DbOrder, backref='line_items')
    product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    product_number: Mapped[ProductNumber] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_products.item_number'),
        index=True,
    )
    product: Mapped[DbProduct] = relationship(
        DbProduct, foreign_keys=[product_id]
    )
    _product_type: Mapped[str] = mapped_column('product_type', db.UnicodeText)
    name: Mapped[str] = mapped_column(db.UnicodeText)
    unit_price: Mapped[Decimal] = mapped_column(db.Numeric(6, 2))
    tax_rate: Mapped[Decimal] = mapped_column(db.Numeric(3, 3))
    quantity: Mapped[int] = mapped_column(db.CheckConstraint('quantity > 0'))
    line_amount: Mapped[Decimal] = mapped_column(db.Numeric(7, 2))
    processing_required: Mapped[bool]
    processing_result: Mapped[Any | None] = mapped_column(db.JSONB)
    processed_at: Mapped[datetime | None]

    def __init__(
        self,
        line_item_id: LineItemID,
        order: DbOrder,
        product_id: ProductID,
        product_number: ProductNumber,
        product_type: ProductType,
        name: str,
        unit_price: Decimal,
        tax_rate: Decimal,
        quantity: int,
        line_amount: Decimal,
        processing_required: bool,
    ) -> None:
        self.id = line_item_id
        # Require order instance rather than order number as argument
        # because line items are created together with the order – and
        # until the order is created, there is no order number assigned.
        self.order = order
        self.product_id = product_id
        self.product_number = product_number
        self._product_type = product_type.name
        self.name = name
        self.unit_price = unit_price
        self.tax_rate = tax_rate
        self.quantity = quantity
        self.line_amount = line_amount
        self.processing_required = processing_required

    @hybrid_property
    def product_type(self) -> ProductType:
        return ProductType[self._product_type]
