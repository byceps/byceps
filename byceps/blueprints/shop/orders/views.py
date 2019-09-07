"""
byceps.blueprints.shop.orders.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ....services.party import service as party_service
from ....services.shop.order import service as order_service
from ....services.shop.shop import service as shop_service
from ....services.snippet.transfer.models import Scope
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authentication.decorators import login_required
from ...snippet.templating import render_snippet_as_partial


blueprint = create_blueprint('shop_orders', __name__)


@blueprint.route('')
@login_required
@templated
def index():
    """List orders placed by the current user for the current party."""
    current_user = g.current_user

    party = party_service.find_party(g.party_id)

    shop = shop_service.find_shop_for_party(party.id)
    if shop:
        orders = order_service.get_orders_placed_by_user_for_shop(
            current_user.id, shop.id)
    else:
        orders = []

    return {
        'party_title': party.title,
        'orders': orders,
    }


@blueprint.route('/<uuid:order_id>')
@login_required
@templated
def view(order_id):
    """Show a single order (if it belongs to the current user and party)."""
    current_user = g.current_user

    order = order_service.find_order_with_details(order_id)

    if order is None:
        abort(404)

    if order.placed_by_id != current_user.id:
        # Order was not placed by the current user.
        abort(404)

    shop = shop_service.get_shop(order.shop_id)
    if shop.party_id != g.party_id:
        # Order does not belong to the current party.
        abort(404)

    template_context = {
        'order': order,
    }

    if order.is_open:
        template_context['payment_instructions'] \
            = _get_payment_instructions(order)

    return template_context


def _get_payment_instructions(order):
    scope = Scope('shop', str(order.shop_id))
    context = {'order_number': order.order_number}

    return render_snippet_as_partial('payment_instructions', scope=scope,
                                     context=context)
