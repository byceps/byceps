"""
byceps.services.shop.cart.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass, field

from moneyed import Money

from moneyed import Currency

from ....util.instances import ReprBuilder

from ..article.transfer.models import Article


@dataclass(frozen=True)
class CartItem:
    """An article with a quantity."""

    article: Article
    quantity: int
    line_amount: Money = field(init=False)

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError('Quantity must be a positive number.')

        object.__setattr__(
            self, 'line_amount', self.article.price * self.quantity
        )


class Cart:
    """A shopping cart."""

    def __init__(self, currency: Currency) -> None:
        self.currency = currency
        self._items: list[CartItem] = []

    def add_item(self, article: Article, quantity: int) -> None:
        article_currency = article.price.currency
        if article_currency != self.currency:
            raise ValueError(
                f'Article currency ({article_currency}) does not match cart currency ({self.currency})'
            )

        item = CartItem(article, quantity)
        self._items.append(item)

    def get_items(self) -> list[CartItem]:
        return self._items

    def calculate_total_amount(self) -> Money:
        if not self._items:
            return self.currency.zero

        return sum(item.line_amount for item in self._items)  # type: ignore[return-value]

    def is_empty(self) -> bool:
        return not self._items

    def __repr__(self) -> str:
        item_count = len(self._items)

        return ReprBuilder(self).add_custom(f'{item_count:d} items').build()
