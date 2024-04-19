"""
byceps.services.shop.article.article_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from moneyed import Money

from byceps.util.result import Err, Ok, Result

from .errors import SomeArticlesLackFixedQuantityError
from .models import Article, ArticleCompilation


def is_article_available_now(article: Article) -> bool:
    """Return `True` if the article is available at this moment in time."""
    start = article.available_from
    end = article.available_until

    now = datetime.utcnow()

    return (start is None or start <= now) and (end is None or now < end)


def calculate_total_amount(
    articles_with_quantities: list[tuple[Article, int]],
) -> Money:
    """Calculate total amount of articles with quantities."""
    if not articles_with_quantities:
        raise ValueError('No articles given')

    return sum(
        article.price * quantity
        for article, quantity in articles_with_quantities
    )  # type: ignore[return-value]


def calculate_article_compilation_total_amount(
    compilation: ArticleCompilation,
) -> Result[Money, SomeArticlesLackFixedQuantityError]:
    """Calculate total amount of articles and their attached articles in
    the compilation.
    """
    if any(item.fixed_quantity is None for item in compilation):
        return Err(SomeArticlesLackFixedQuantityError())

    articles_with_quantities = [
        (item.article, item.fixed_quantity) for item in compilation
    ]

    total_amount = calculate_total_amount(articles_with_quantities)

    return Ok(total_amount)
