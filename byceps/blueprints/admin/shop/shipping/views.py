"""
byceps.blueprints.admin.shop.shipping.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from .....services.brand import brand_service
from .....services.shop.article import article_service
from .....services.shop.shipping import shipping_service
from .....services.shop.shop import shop_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import permission_required


blueprint = create_blueprint('shop_shipping_admin', __name__)


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop_order.view')
@templated
def view_for_shop(shop_id):
    """List the articles to ship, or likely to ship, for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    articles_to_ship = shipping_service.get_articles_to_ship(shop.id)
    article_ids = {ats.article_id for ats in articles_to_ship}
    articles = article_service.get_articles(article_ids)
    articles_by_id = {article.id: article for article in articles}

    return {
        'shop': shop,
        'brand': brand,
        'articles_to_ship': articles_to_ship,
        'articles_by_id': articles_by_id,
    }


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
