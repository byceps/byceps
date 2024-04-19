"""
byceps.services.shop.article.article_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from moneyed import Money

from byceps.services.shop.cart.models import Cart
from byceps.util.result import Err, Ok, Result

from .errors import SomeArticlesLackFixedQuantityError
from .models import Article, ArticleCompilation


def is_article_available_now(article: Article) -> bool:
    """Return `True` if the article is available at this moment in time."""
    start = article.available_from
    end = article.available_until

    now = datetime.utcnow()

    return (start is None or start <= now) and (end is None or now < end)


def calculate_article_compilation_total_amount(
    compilation: ArticleCompilation,
) -> Result[Money, SomeArticlesLackFixedQuantityError]:
    """Calculate total amount of articles and their attached articles in
    the compilation.
    """
    if any(item.fixed_quantity is None for item in compilation):
        return Err(SomeArticlesLackFixedQuantityError())

    cart = Cart(compilation._items[0].article.price.currency)

    for item in compilation:
        cart.add_item(item.article, item.fixed_quantity)

    total_amount = cart.calculate_total_amount()
    return Ok(total_amount)
