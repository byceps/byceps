"""
byceps.services.shop.cart.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import Currency, Money

from byceps.services.shop.article.models import Article, ArticleWithQuantity
from byceps.util.instances import ReprBuilder


class Cart:
    """A shopping cart."""

    def __init__(self, currency: Currency) -> None:
        self.currency = currency
        self._items: list[ArticleWithQuantity] = []

    def add_item(self, article: Article, quantity: int) -> None:
        article_currency = article.price.currency
        if article_currency != self.currency:
            raise ValueError(
                f'Article currency ({article_currency}) does not match cart currency ({self.currency})'
            )

        item = ArticleWithQuantity(article, quantity)
        self._items.append(item)

    def get_items(self) -> list[ArticleWithQuantity]:
        return self._items

    def calculate_total_amount(self) -> Money:
        if not self._items:
            return self.currency.zero

        return sum(item.amount for item in self._items)  # type: ignore[return-value]

    def is_empty(self) -> bool:
        return not self._items

    def __repr__(self) -> str:
        item_count = len(self._items)

        return ReprBuilder(self).add_custom(f'{item_count:d} items').build()
