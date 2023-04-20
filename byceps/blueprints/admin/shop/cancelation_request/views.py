"""
byceps.blueprints.admin.shop.cancelation_request.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request

from byceps.services.brand import brand_service
from byceps.services.shop.cancelation_request import cancelation_request_service
from byceps.services.shop.order import order_service
from byceps.services.shop.shop import shop_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('shop_cancelation_request_admin', __name__)


@blueprint.get('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.get('/for_shop/<shop_id>/pages/<int:page>')
@permission_required('shop_order.view')
@templated
def index(shop_id, page):
    """Show cancelation requests for a shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    per_page = request.args.get('per_page', type=int, default=10)

    requests = cancelation_request_service.get_all_requests_for_shop_paginated(
        shop.id, page, per_page
    )

    order_numbers = {request.order_number for request in requests.items}
    orders = order_service.get_orders_for_order_numbers(order_numbers)
    orders_by_order_number = {order.order_number: order for order in orders}

    orderer_ids = {order.placed_by_id for order in orders}
    orderers = user_service.get_users_for_admin(orderer_ids)
    orderers_by_id = user_service.index_users_by_id(orderers)

    donation_extent_totals = {
        de.name: count
        for de, count in cancelation_request_service.get_donation_extent_totals_for_shop(
            shop.id
        ).items()
    }

    donations_total = cancelation_request_service.get_donation_sum_for_shop(
        shop.id
    )

    request_quantities_by_state = (
        cancelation_request_service.get_request_quantities_by_state(shop.id)
    )

    return {
        'shop': shop,
        'brand': brand,
        'requests': requests,
        'orders_by_order_number': orders_by_order_number,
        'orderers_by_id': orderers_by_id,
        'per_page': per_page,
        'donation_extent_totals': donation_extent_totals,
        'donations_total': donations_total,
        'request_quantities_by_state': request_quantities_by_state,
    }


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
