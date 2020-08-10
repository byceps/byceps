"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.article import service as article_service
from byceps.services.shop.shop import service as shop_service
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope

from testfixtures.shop_article import create_article as _create_article

from tests.helpers import DEFAULT_EMAIL_CONFIG_ID


def create_shop(shop_id='shop-1', email_config_id=DEFAULT_EMAIL_CONFIG_ID):
    return shop_service.create_shop(shop_id, shop_id, email_config_id)


def create_shop_fragment(shop_id, admin_id, name, body):
    scope = Scope('shop', shop_id)

    version, _ = snippet_service.create_fragment(scope, name, admin_id, body)

    return version.snippet_id


def create_article(shop_id, **kwargs):
    article = _create_article(shop_id, **kwargs)

    return article_service.create_article(
        shop_id,
        article.item_number,
        article.description,
        article.price,
        article.tax_rate,
        article.total_quantity,
        article.max_quantity_per_order,
    )
