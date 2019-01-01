"""
byceps.services.shop.shipping.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from ...article.transfer.models import ArticleNumber


@attrs(frozen=True, slots=True)
class ArticleToShip:
    article_number = attrib(type=ArticleNumber)
    description = attrib(type=str)
    quantity_paid = attrib(type=int)
    quantity_open = attrib(type=int)
    quantity_total = attrib(type=int)
