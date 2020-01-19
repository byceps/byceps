"""
byceps.services.shop.shipping.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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
