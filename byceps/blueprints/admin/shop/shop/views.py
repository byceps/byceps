"""
byceps.blueprints.admin.shop.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request, url_for

from .....services.brand import service as brand_service
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import PaymentState
from .....services.shop.shop import service as shop_service
from .....util.authorization import register_permission_enum
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
)

from .authorization import ShopPermission


blueprint = create_blueprint('shop_shop_admin', __name__)


register_permission_enum(ShopPermission)


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def view(shop_id):
    """Show the shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    order_counts_by_payment_state = order_service.count_orders_per_payment_state(
        shop.id
    )

    return {
        'shop': shop,
        'brand': brand,

        'order_counts_by_payment_state': order_counts_by_payment_state,
        'PaymentState': PaymentState,

        'settings': shop.extra_settings,
    }


@blueprint.route('/for_brand/<brand_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_brand(brand_id):
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    shop = shop_service.find_shop_for_brand(brand.id)
    if shop is not None:
        return redirect_to('.view', shop_id=shop.id)

    return {
        'brand': brand,
    }


@blueprint.route('/for_brand/<brand_id>', methods=['POST'])
@permission_required(ShopPermission.create)
@respond_no_content_with_location
def create(brand_id):
    """Create a shop."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    shop_id = brand.id
    title = brand.title

    shop = shop_service.create_shop(shop_id, brand.id, title)

    flash_success(f'Der Shop wurde angelegt.')
    return url_for('.view', shop_id=shop.id)


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
