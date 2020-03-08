"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.article import service as article_service
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope

from testfixtures.shop_article import create_article as _create_article


def create_shop_fragment(shop_id, admin_id, name, body):
    scope = Scope('shop', shop_id)

    snippet_service.create_fragment(scope, name, admin_id, body)


def create_article(shop_id, **kwargs):
    article = _create_article(shop_id, **kwargs)

    return article_service.create_article(
        shop_id,
        article.item_number,
        article.description,
        article.price,
        article.tax_rate,
        article.quantity,
    )
