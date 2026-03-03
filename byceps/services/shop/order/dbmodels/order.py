"""
byceps.services.shop.order.dbmodels.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from moneyed import Currency, get_currency, Money
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import (
    LineItemID,
    OrderID,
    PaymentState,
)
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import (
    ProductID,
    ProductNumber,
    ProductType,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.dbmodels import DbStorefront
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.dbmodels import DbUser
from byceps.services.user.models import UserID
from byceps.util.instances import ReprBuilder


class DbOrder(db.Model):
    """An order for products, placed by a user."""

    __tablename__ = 'shop_orders'

    id: Mapped[OrderID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    storefront_id: Mapped[StorefrontID] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_storefronts.id'),
        index=True,
    )
    storefront: Mapped[DbStorefront] = relationship()
    order_number: Mapped[OrderNumber] = mapped_column(
        db.UnicodeText, unique=True
    )
    placed_by_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    placed_by: Mapped[DbUser] = relationship(foreign_keys=[placed_by_id])
    company: Mapped[str | None] = mapped_column(db.UnicodeText)
    first_name: Mapped[str] = mapped_column(db.UnicodeText)
    last_name: Mapped[str] = mapped_column(db.UnicodeText)
    country: Mapped[str] = mapped_column(db.UnicodeText)
    postal_code: Mapped[str] = mapped_column(db.UnicodeText)
    city: Mapped[str] = mapped_column(db.UnicodeText)
    street: Mapped[str] = mapped_column(db.UnicodeText)
    _currency: Mapped[str] = mapped_column('currency', db.UnicodeText)
    _total_amount: Mapped[Decimal] = mapped_column(
        'total_amount', db.Numeric(7, 2)
    )
    invoice_created_at: Mapped[datetime | None]
    payment_method: Mapped[str | None] = mapped_column(db.UnicodeText)
    _payment_state: Mapped[str] = mapped_column(
        'payment_state', db.UnicodeText, index=True
    )
    payment_state_updated_at: Mapped[datetime | None]
    payment_state_updated_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    payment_state_updated_by: Mapped[DbUser] = relationship(
        foreign_keys=[payment_state_updated_by_id]
    )
    cancellation_reason: Mapped[str | None] = mapped_column(db.UnicodeText)
    processing_required: Mapped[bool]
    processed_at: Mapped[datetime | None]

    def __init__(
        self,
        order_id: OrderID,
        created_at: datetime,
        shop_id: ShopID,
        storefront_id: StorefrontID,
        order_number: OrderNumber,
        placed_by_id: UserID,
        company: str | None,
        first_name: str,
        last_name: str,
        country: str,
        postal_code: str,
        city: str,
        street: str,
        total_amount: Money,
        processing_required: bool,
    ) -> None:
        self.id = order_id
        self.created_at = created_at
        self.shop_id = shop_id
        self.storefront_id = storefront_id
        self.order_number = order_number
        self.placed_by_id = placed_by_id
        self.company = company
        self.first_name = first_name
        self.last_name = last_name
        self.country = country
        self.postal_code = postal_code
        self.city = city
        self.street = street
        self.currency = total_amount.currency
        self._total_amount = total_amount.amount
        self.payment_state = PaymentState.open
        self.processing_required = processing_required

    @hybrid_property
    def currency(self) -> Currency:
        return get_currency(self._currency)

    @currency.setter
    def currency(self, currency: Currency) -> None:
        self._currency = currency.code

    @property
    def total_amount(self) -> Money:
        return Money(self._total_amount, self.currency)

    @hybrid_property
    def payment_state(self) -> PaymentState:
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state: PaymentState) -> None:
        self._payment_state = state.name

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('order_number')
            .add_custom(self.payment_state.name)
            .build()
        )


class DbLineItem(db.Model):
    """A line item that belongs to an order."""

    __tablename__ = 'shop_order_line_items'

    id: Mapped[LineItemID] = mapped_column(db.Uuid, primary_key=True)
    order_number: Mapped[OrderNumber] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_orders.order_number'),
        index=True,
    )
    order: Mapped[DbOrder] = relationship(backref='line_items')
    product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    product_number: Mapped[ProductNumber] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_products.item_number'),
        index=True,
    )
    product: Mapped[DbProduct] = relationship(foreign_keys=[product_id])
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
