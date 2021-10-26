"""
byceps.blueprints.site.dashboard.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Current user's dashboard

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask import abort, g

from ....services.authentication.session.models.current_user import CurrentUser
from ....services.board.dbmodels.topic import Topic as DbTopic
from ....services.board import (
    access_control_service as board_access_control_service,
    topic_query_service as board_topic_query_service,
)
from ....services.guest_server import service as guest_server_service
from ....services.news import service as news_item_service
from ....services.news.transfer.models import Headline as NewsHeadline
from ....services.shop.order import service as order_service
from ....services.shop.order.transfer.models import Order
from ....services.shop.storefront import service as storefront_service
from ....services.site import service as site_service
from ....services.site.transfer.models import Site
from ....services.ticketing import ticket_service
from ....services.ticketing.dbmodels.ticket import Ticket as DbTicket
from ....services.user import service as user_service
from ....typing import UserID
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import login_required

from ..board import service as board_helper_service


blueprint = create_blueprint('dashboard', __name__)


@blueprint.get('')
@login_required
@templated
def index():
    """Show current user's dashboard."""
    user = user_service.find_active_user(g.user.id)
    if user is None:
        abort(404)

    site = site_service.get_site(g.site_id)

    open_orders = _get_open_orders(site, user.id)
    tickets = _get_tickets(user.id)
    news_headlines = _get_news_headlines(site)
    board_topics = _get_board_topics(site, g.user)
    guest_servers = guest_server_service.get_servers_for_owner_and_party(
        g.user.id, g.party_id
    )
    guest_server_setting = guest_server_service.get_setting_for_party(
        g.party_id
    )

    return {
        'open_orders': open_orders,
        'tickets': tickets,
        'news_headlines': news_headlines,
        'board_topics': board_topics,
        'guest_servers': guest_servers,
        'guest_server_setting': guest_server_setting,
    }


def _get_open_orders(site: Site, user_id: UserID) -> list[Order]:
    storefront_id = site.storefront_id
    if storefront_id is None:
        return []

    storefront = storefront_service.get_storefront(storefront_id)

    orders = order_service.get_orders_placed_by_user_for_shop(
        user_id, storefront.shop_id
    )

    orders = [order for order in orders if order.is_open]

    return orders


def _get_tickets(user_id: UserID) -> list[DbTicket]:
    if g.party_id is None:
        return []

    return ticket_service.find_tickets_used_by_user(user_id, g.party_id)


def _get_news_headlines(site: Site) -> list[NewsHeadline]:
    channel_ids = site.news_channel_ids
    if not channel_ids:
        return []

    return news_item_service.get_recent_headlines(channel_ids, limit=4)


def _get_board_topics(site: Site, current_user: CurrentUser) -> list[DbTopic]:
    board_id = site.board_id
    if board_id is None:
        return []

    has_access = board_access_control_service.has_user_access_to_board(
        current_user.id, board_id
    )
    if not has_access:
        return []

    include_hidden = board_helper_service.may_current_user_view_hidden()
    topics = board_topic_query_service.get_recent_topics(
        board_id, include_hidden, limit=6
    )

    board_helper_service.add_topic_unseen_flag(topics, current_user)

    return topics
