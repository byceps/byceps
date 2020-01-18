"""
testfixtures.shop_article
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from byceps.services.shop.article.models.article import Article


ANY_ARTICLE_ITEM_NUMBER = 'AEC-05-A00009'


def create_article(
    shop_id,
    *,
    item_number=ANY_ARTICLE_ITEM_NUMBER,
    description='Cool thing',
    price=None,
    tax_rate=None,
    available_from=None,
    available_until=None,
    quantity=1,
):
    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return Article(
        shop_id,
        item_number,
        description,
        price,
        tax_rate,
        quantity,
        available_from=available_from,
        available_until=available_until,
    )
