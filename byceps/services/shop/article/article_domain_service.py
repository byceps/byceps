"""
byceps.services.shop.article.article_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from moneyed import Money

from byceps.services.shop.cart.models import Cart

from .models import Article, ArticleCompilation


def is_article_available_now(article: Article) -> bool:
    """Return `True` if the article is available at this moment in time."""
    start = article.available_from
    end = article.available_until

    now = datetime.utcnow()

    return (start is None or start <= now) and (end is None or now < end)


def calculate_article_compilation_total_amount(
    compilation: ArticleCompilation,
) -> Money:
    """Calculate total amount of articles and their attached articles in
    the compilation.
    """
    cart = Cart(compilation._items[0].article.price.currency)
    _copy_article_compilation_to_cart(compilation, cart)
    return cart.calculate_total_amount()


def _copy_article_compilation_to_cart(
    compilation: ArticleCompilation, cart: Cart
) -> None:
    for compilation_item in compilation:
        if compilation_item.fixed_quantity is None:
            raise ValueError(
                'Für einige Artikel ist keine Stückzahl vorgegeben.'
            )

        cart.add_item(compilation_item.article, compilation_item.fixed_quantity)
