"""
byceps.services.shop.cart.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import Currency

from byceps.services.shop.product.models import Product, ProductWithQuantity


class Cart:
    """A shopping cart."""

    def __init__(self, currency: Currency) -> None:
        self.currency = currency
        self._items: list[ProductWithQuantity] = []

    def add_item(self, product: Product, quantity: int) -> None:
        product_currency = product.price.currency
        if product_currency != self.currency:
            raise ValueError(
                f'Product currency ({product_currency}) does not match cart currency ({self.currency})'
            )

        item = ProductWithQuantity(product, quantity)
        self._items.append(item)

    def get_items(self) -> list[ProductWithQuantity]:
        return self._items

    def is_empty(self) -> bool:
        return not self._items
