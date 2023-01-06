"""
byceps.services.shop.shipping.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from ...article.transfer.models import ArticleID


@dataclass(frozen=True)
class ArticleToShip:
    article_id: ArticleID
    description: str
    quantity_paid: int
    quantity_open: int
    quantity_total: int
