"""
byceps.blueprints.admin.shop.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from flask import abort

from .....services.shop.article import service as article_service
from .....services.shop.order import (
    action_service as order_action_service,
    service as order_service,
)
from .....services.shop.order.transfer.models import PaymentState
from .....services.shop.shop import service as shop_service
from .....services.site import service as site_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import redirect_to

from ....authorization.decorators import permission_required
from ....authorization.registry import permission_registry

from .authorization import ShopPermission


blueprint = create_blueprint('shop_shop_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/')
@permission_required(ShopPermission.view)
@templated
def index():
    """List all shops."""
    shops = shop_service.get_all_shops()

    return {
        'shops': shops,
    }


@blueprint.route('/for_site/<site_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_site(site_id):
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    if site.shop_id is not None:
        shop = shop_service.get_shop(site.id)
        return redirect_to('.view_for_shop', shop_id=shop.id)

    return {
        'site': site,
    }


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_shop(shop_id):
    """Show the shop."""
    shop = _get_shop_or_404(shop_id)

    order_counts_by_payment_state = order_service.count_orders_per_payment_state(
        shop.id
    )

    order_actions_by_article_number = _get_order_actions_by_article_number(
        shop.id
    )

    return {
        'shop': shop,

        'order_counts_by_payment_state': order_counts_by_payment_state,
        'PaymentState': PaymentState,

        'settings': shop.extra_settings,

        'order_actions_by_article_number': order_actions_by_article_number,
    }


def _get_order_actions_by_article_number(shop_id):
    actions = order_action_service.get_actions(shop_id)

    actions.sort(key=lambda a: a.payment_state.name, reverse=True)
    actions.sort(key=lambda a: a.article_number)

    actions_by_article_number = defaultdict(list)
    for action in actions:
        actions_by_article_number[action.article_number].append(action)

    return actions_by_article_number


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
