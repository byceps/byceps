"""
byceps.services.shop.shipping.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from ...article.transfer.models import ArticleNumber


@dataclass(frozen=True)
class ArticleToShip:
    article_number: ArticleNumber
    description: str
    quantity_paid: int
    quantity_open: int
    quantity_total: int
