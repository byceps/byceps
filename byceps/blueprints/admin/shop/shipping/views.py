"""
byceps.blueprints.admin.shop.shipping.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from .....services.shop.shipping import service as shipping_service
from .....services.shop.shop import service as shop_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated

from ....common.authorization.decorators import permission_required

from ..order.authorization import ShopOrderPermission


blueprint = create_blueprint('shop_shipping_admin', __name__)


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopOrderPermission.view)
@templated
def view_for_shop(shop_id):
    """List the articles to ship, or likely to ship, for that shop."""
    shop = _get_shop_or_404(shop_id)

    articles_to_ship = shipping_service.get_articles_to_ship(shop.id)

    return {
        'shop': shop,
        'articles_to_ship': articles_to_ship,
    }


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
