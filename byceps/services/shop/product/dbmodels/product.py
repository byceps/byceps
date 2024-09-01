"""
byceps.services.shop.product.dbmodels.product
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from moneyed import Currency, get_currency, Money
from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.product.models import (
    ProductID,
    ProductNumber,
    ProductType,
    ProductTypeParams,
)
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder


class DbProduct(db.Model):
    """A product that can be bought."""

    __tablename__ = 'shop_products'
    __table_args__ = (
        db.UniqueConstraint('shop_id', 'name'),
        db.CheckConstraint('available_from < available_until'),
    )

    id: Mapped[ProductID] = mapped_column(db.Uuid, primary_key=True)
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    item_number: Mapped[ProductNumber] = mapped_column(
        db.UnicodeText, unique=True
    )
    _type: Mapped[str] = mapped_column('type', db.UnicodeText)
    type_params: Mapped[ProductTypeParams | None] = mapped_column(db.JSONB)
    name: Mapped[str] = mapped_column(db.UnicodeText)
    price_amount: Mapped[Decimal] = mapped_column(db.Numeric(6, 2))
    _price_currency: Mapped[str] = mapped_column(
        'price_currency', db.UnicodeText
    )
    tax_rate: Mapped[Decimal] = mapped_column(db.Numeric(3, 3))
    available_from: Mapped[datetime | None]
    available_until: Mapped[datetime | None]
    total_quantity: Mapped[int]
    quantity: Mapped[int] = mapped_column(db.CheckConstraint('quantity >= 0'))
    max_quantity_per_order: Mapped[int]
    not_directly_orderable: Mapped[bool]
    separate_order_required: Mapped[bool]
    processing_required: Mapped[bool]
    archived: Mapped[bool]

    def __init__(
        self,
        product_id: ProductID,
        shop_id: ShopID,
        item_number: ProductNumber,
        type_: ProductType,
        name: str,
        price: Money,
        tax_rate: Decimal,
        total_quantity: int,
        max_quantity_per_order: int,
        processing_required: bool,
        *,
        type_params: ProductTypeParams | None = None,
        available_from: datetime | None = None,
        available_until: datetime | None = None,
        not_directly_orderable: bool = False,
        separate_order_required: bool = False,
        archived: bool = False,
    ) -> None:
        self.id = product_id
        self.shop_id = shop_id
        self.item_number = item_number
        self._type = type_.name
        self.type_params = type_params
        self.name = name
        self.price_amount = price.amount
        self.price_currency = price.currency
        self.tax_rate = tax_rate
        self.available_from = available_from
        self.available_until = available_until
        self.total_quantity = total_quantity
        self.quantity = total_quantity  # Initialize with total quantity.
        self.max_quantity_per_order = max_quantity_per_order
        self.not_directly_orderable = not_directly_orderable
        self.separate_order_required = separate_order_required
        self.processing_required = processing_required
        self.archived = archived

    @hybrid_property
    def type_(self) -> ProductType:
        return ProductType[self._type]

    @hybrid_property
    def price_currency(self) -> Currency:
        return get_currency(self._price_currency)

    @price_currency.setter
    def price_currency(self, currency: Currency) -> None:
        self._price_currency = currency.code

    @property
    def price(self) -> Money:
        return Money(self.price_amount, self.price_currency)

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('item_number')
            .add_with_lookup('name')
            .build()
        )
