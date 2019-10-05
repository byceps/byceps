"""
byceps.blueprints.admin.ticketing.checkin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from flask import abort, request

from .....services.party import service as party_service
from .....services.shop.order import service as order_service
from .....services.shop.shop import service as shop_service
from .....services.ticketing import ticket_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated

from ....authorization.decorators import permission_required

from ...shop.order import service as order_blueprint_service
from ...ticketing.authorization import TicketingPermission
from ...user import service as user_blueprint_service


blueprint = create_blueprint('ticketing_checkin', __name__)


MINIMUM_AGE_IN_YEARS = 18


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
        latest_dob_for_checkin = _get_latest_date_of_birth_for_checkin()
        tickets = _search_tickets(party.id, search_term, limit)
        orders = _search_orders(party.shop_id, search_term, limit)
        users = _search_users(party.id, search_term, limit)

        tickets += list(_get_tickets_for_users(party.id, users))
    else:
        latest_dob_for_checkin = None
        tickets = None
        orders = None
        users = None

    return {
        'party': party,
        'latest_dob_for_checkin': latest_dob_for_checkin,
        'search_term': search_term,
        'tickets': tickets,
        'orders': orders,
        'users': users,
    }


def _get_latest_date_of_birth_for_checkin():
    today = date.today()
    return today.replace(year=today.year - MINIMUM_AGE_IN_YEARS)


def _search_tickets(party_id, search_term, limit):
    page = 1
    per_page = limit

    tickets_pagination = ticket_service.get_tickets_with_details_for_party_paginated(
        party_id, page, per_page, search_term=search_term
    )

    return tickets_pagination.items


def _search_orders(shop_id, search_term, limit):
    if shop_id is None:
        return []

    shop = shop_service.get_shop(shop_id)

    page = 1
    per_page = limit

    orders_pagination = order_service.get_orders_for_shop_paginated(
        shop.id, page, per_page, search_term=search_term
    )

    # Replace order objects with order tuples.
    orders = [order.to_transfer_object() for order in orders_pagination.items]

    orders = list(
        order_blueprint_service.extend_order_tuples_with_orderer(orders)
    )

    return orders


def _search_users(party_id, search_term, limit):
    page = 1
    per_page = limit

    users_pagination = user_blueprint_service.get_users_paginated(
        page, per_page, search_term=search_term
    )

    # Exclude deleted users.
    users_pagination.items = [
        user for user in users_pagination.items if not user.deleted
    ]

    return users_pagination.items


def _get_tickets_for_users(party_id, users):
    for user in users:
        yield from ticket_service.find_tickets_used_by_user_simplified(
            user.id, party_id
        )
