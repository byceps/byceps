"""
byceps.services.shop.article.models.compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator, List, Optional

from ..transfer.models import Article


class ArticleCompilationItem:
    def __init__(
        self, article: Article, *, fixed_quantity: Optional[int] = None
    ) -> None:
        if (fixed_quantity is not None) and fixed_quantity < 1:
            raise ValueError(
                'Fixed quantity, if given, must be a positive number.'
            )

        self.article = article
        self.fixed_quantity = fixed_quantity

    def has_fixed_quantity(self) -> bool:
        return self.fixed_quantity is not None


class ArticleCompilation:

    def __init__(self) -> None:
        self._items: List[ArticleCompilationItem] = []

    def append(self, item: ArticleCompilationItem) -> None:
        self._items.append(item)

    def __iter__(self) -> Iterator[ArticleCompilationItem]:
        return iter(self._items)

    def is_empty(self) -> bool:
        return not self._items
