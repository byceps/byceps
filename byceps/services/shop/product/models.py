"""
byceps.services.shop.product.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NewType
from uuid import UUID

from flask_babel import lazy_gettext
from moneyed import Money

from byceps.services.shop.shop.models import ShopID


ProductID = NewType('ProductID', UUID)


ProductNumber = NewType('ProductNumber', str)


ProductNumberSequenceID = NewType('ProductNumberSequenceID', UUID)


@dataclass(frozen=True)
class ProductNumberSequence:
    id: ProductNumberSequenceID
    shop_id: ShopID
    prefix: str
    value: int
    archived: bool


ProductType = Enum(
    'ProductType', ['physical', 'ticket', 'ticket_bundle', 'other']
)


_PRODUCT_TYPE_LABELS = {
    ProductType.physical: lazy_gettext('physical'),
    ProductType.ticket: lazy_gettext('Ticket'),
    ProductType.ticket_bundle: lazy_gettext('Ticket bundle'),
    ProductType.other: lazy_gettext('other'),
}


def get_product_type_label(product_type: ProductType) -> str:
    """Return a label for the product type."""
    return _PRODUCT_TYPE_LABELS[product_type]


ProductTypeParams = dict[str, str | int]


ProductImageID = NewType('ProductImageID', UUID)


AttachedProductID = NewType('AttachedProductID', UUID)


@dataclass(frozen=True)
class Product:
    id: ProductID
    shop_id: ShopID
    item_number: ProductNumber
    type_: ProductType
    type_params: ProductTypeParams
    name: str
    price: Money
    tax_rate: Decimal
    available_from: datetime | None
    available_until: datetime | None
    total_quantity: int
    quantity: int
    max_quantity_per_order: int
    not_directly_orderable: bool
    separate_order_required: bool
    processing_required: bool
    archived: bool


@dataclass(frozen=True)
class ProductImage:
    id: ProductImageID
    product_id: ProductID
    url: str
    url_preview: str
    position: int


@dataclass(frozen=True)
class ProductAttachment:
    attached_product: Product
    attached_quantity: int


@dataclass(frozen=True, slots=True)
class ProductWithQuantity:
    product: Product
    quantity: int
    amount: Money = field(init=False)

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError('Quantity must be a positive number.')

        object.__setattr__(self, 'amount', self.product.price * self.quantity)


@dataclass(frozen=True)
class ProductCompilationItem:
    product: Product
    fixed_quantity: int | None = None

    def __post_init__(self) -> None:
        if (self.fixed_quantity is not None) and (self.fixed_quantity < 1):
            raise ValueError(
                'Fixed quantity, if given, must be a positive number.'
            )

    @property
    def has_fixed_quantity(self) -> bool:
        return self.fixed_quantity is not None


class ProductCompilation:
    def __init__(self, items: list[ProductCompilationItem]) -> None:
        if not items:
            raise ValueError('Product compilation must not be empty')

        self._items = list(items)

    def __iter__(self) -> Iterator[ProductCompilationItem]:
        return iter(self._items)


class ProductCompilationBuilder:
    def __init__(self) -> None:
        self._items: list[ProductCompilationItem] = []

    def append_product(
        self, product: Product, *, fixed_quantity: int | None = None
    ) -> None:
        item = ProductCompilationItem(product, fixed_quantity=fixed_quantity)
        self._items.append(item)

    def build(self) -> ProductCompilation:
        return ProductCompilation(self._items)
