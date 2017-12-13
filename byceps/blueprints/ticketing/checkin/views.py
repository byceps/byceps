"""
byceps.blueprints.ticketing.checkin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.party import service as party_service
from ....services.shop.order import service as order_service
from ....services.ticketing import ticket_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry
from ...shop_order_admin import service as order_blueprint_service
from ...ticketing_admin.authorization import TicketingPermission
from ...user_admin import service as user_blueprint_service


blueprint = create_blueprint('ticketing_checkin', __name__)


@blueprint.route('/for_party/<party_id>')
@permission_required(TicketingPermission.checkin)
@templated
def index(party_id):
    """Provide form to find tickets, then check them in."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    search_term = request.args.get('search_term', default='').strip()

    limit = 10

    if search_term:
        tickets = _search_tickets(party.id, search_term, limit)
        orders = _search_orders(party.id, search_term, limit)
        users = _search_users(party.id, search_term, limit)
    else:
        tickets = None
        orders = None
        orderers_by_id = None
        users = None

    return {
        'party': party,
        'search_term': search_term,
        'tickets': tickets,
        'orders': orders,
        'users': users,
    }


def _search_tickets(party_id, search_term, limit):
    page = 1
    per_page = limit

    tickets_pagination = ticket_service.get_tickets_with_details_for_party_paginated(
        party_id, page, per_page, search_term=search_term)

    return tickets_pagination.items


def _search_orders(party_id, search_term, limit):
    page = 1
    per_page = limit

    orders_pagination = order_service.get_orders_for_party_paginated(
        party_id, page, per_page, search_term=search_term)

    # Replace order objects with order tuples.
    orders = [order.to_tuple() for order in orders_pagination.items]

    orders = list(order_blueprint_service.extend_order_tuples_with_orderer(
        orders))

    return orders


def _search_users(party_id, search_term, limit):
    page = 1
    per_page = limit

    users_pagination = user_blueprint_service.get_users_paginated(
        page, per_page, search_term=search_term)

    return users_pagination.items
