"""
byceps.services.shop.shipping.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from byceps.services.brand import brand_service
from byceps.services.shop.product import product_service
from byceps.services.shop.shipping import shipping_service
from byceps.services.shop.shop import shop_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('shop_shipping_admin', __name__)


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop_order.view')
@templated
def view_for_shop(shop_id):
    """List the products to ship, or likely to ship, for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    products_to_ship = shipping_service.get_products_to_ship(shop.id)
    product_ids = {pts.product_id for pts in products_to_ship}
    products = product_service.get_products(product_ids)
    products_by_id = {product.id: product for product in products}

    return {
        'shop': shop,
        'brand': brand,
        'products_to_ship': products_to_ship,
        'products_by_id': products_by_id,
    }


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
