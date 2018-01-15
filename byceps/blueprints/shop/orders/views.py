"""
byceps.blueprints.shop.orders.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ....services.party import service as party_service
from ....services.shop.order import service as order_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authentication.decorators import login_required


blueprint = create_blueprint('shop_orders', __name__)


@blueprint.route('')
@login_required
@templated
def index():
    """List orders placed by the current user for the current party."""
    current_user = g.current_user

    party = party_service.find_party(g.party_id)

    orders = order_service.get_orders_placed_by_user_for_party(
        current_user.id, party.id)

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

    if order.party_id != g.party_id:
        # Order was not placed by the current user.
        abort(404)

    placed_by = user_service.find_user(order.placed_by_id)

    return {
        'order': order,
        'placed_by': placed_by,
    }
