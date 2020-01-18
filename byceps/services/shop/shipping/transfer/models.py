"""
byceps.services.shop.shipping.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrs

from ...article.transfer.models import ArticleNumber


@attrs(auto_attribs=True, frozen=True, slots=True)
class ArticleToShip:
    article_number: ArticleNumber
    description: str
    quantity_paid: int
    quantity_open: int
    quantity_total: int
