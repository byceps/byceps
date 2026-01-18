"""
byceps.services.dashboard.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Current user's dashboard

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from flask import abort, g

from byceps.services.board.blueprints.site import (
    service as board_helper_service,
)
from byceps.services.guest_server import guest_server_service
from byceps.services.guest_server.blueprints.site.views import _sort_addresses
from byceps.services.guest_server.models import Server
from byceps.services.news import news_item_service
from byceps.services.news.models import NewsHeadline
from byceps.services.shop.order import order_service
from byceps.services.shop.order.models.order import SiteOrderListItem
from byceps.services.shop.storefront import storefront_service
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.user import user_service
from byceps.services.user.models.user import UserID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import login_required


blueprint = create_blueprint('dashboard', __name__)


@blueprint.get('')
@login_required
@templated
def index():
    """Show current user's dashboard."""
    user = user_service.find_active_user(g.user.id)
    if user is None:
        abort(404)

    open_orders = _get_open_orders(user.id)
    tickets = _get_tickets(user.id)
    news_headlines = _get_news_headlines()
    board_topics = board_helper_service.get_recent_topics(g.user)
    guest_servers = _get_guest_servers()

    return {
        'open_orders': open_orders,
        'tickets': tickets,
        'news_headlines': news_headlines,
        'board_topics': board_topics,
        'guest_servers': guest_servers,
        'sort_guest_server_addresses': _sort_addresses,
    }


def _get_open_orders(user_id: UserID) -> list[SiteOrderListItem]:
    storefront_id = g.site.storefront_id
    if storefront_id is None:
        return []

    storefront = storefront_service.get_storefront(storefront_id)

    orders = order_service.get_orders_placed_by_user_for_storefront(
        user_id, storefront.id
    )

    orders = [order for order in orders if order.is_open]

    return orders


def _get_tickets(user_id: UserID) -> Sequence[DbTicket]:
    if not g.party:
        return []

    return ticket_service.get_tickets_used_by_user(user_id, g.party.id)


def _get_news_headlines() -> list[NewsHeadline] | None:
    channel_ids = g.site.news_channel_ids
    if not channel_ids:
        return None

    return news_item_service.get_recent_headlines(channel_ids, limit=4)


def _get_guest_servers() -> list[Server] | None:
    if not g.party:
        return None

    return guest_server_service.get_servers_for_owner_and_party(
        g.user.id, g.party.id
    )
