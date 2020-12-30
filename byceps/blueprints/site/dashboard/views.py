"""
byceps.blueprints.site.dashboard.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Current user's dashboard

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List

from flask import abort, g

from ....services.authentication.session.models.current_user import CurrentUser
from ....services.board.models.topic import Topic as DbTopic
from ....services.board import (
    access_control_service as board_access_control_service,
    topic_query_service as board_topic_query_service,
)
from ....services.news import service as news_item_service
from ....services.news.transfer.models import Headline as NewsHeadline
from ....services.site import service as site_service
from ....services.site.transfer.models import Site
from ....services.ticketing import ticket_service
from ....services.ticketing.models.ticket import Ticket as DbTicket
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...common.authentication.decorators import login_required

from ..board import service as board_helper_service


blueprint = create_blueprint('dashboard', __name__)


@blueprint.route('')
@login_required
@templated
def index():
    """Show current user's dashboard."""
    user = user_service.find_active_db_user(g.current_user.id)
    if user is None:
        abort(404)

    site = site_service.get_site(g.site_id)

    tickets = _get_tickets(g.current_user)
    news_headlines = _get_news_headlines(site)
    board_topics = _get_board_topics(site, g.current_user)

    return {
        'tickets': tickets,
        'news_headlines': news_headlines,
        'board_topics': board_topics,
    }


def _get_tickets(current_user: CurrentUser) -> List[DbTicket]:
    if g.party_id is None:
        return []

    return ticket_service.find_tickets_used_by_user(current_user.id, g.party_id)


def _get_news_headlines(site: Site) -> List[NewsHeadline]:
    channel_id = site.news_channel_id
    if channel_id is None:
        return []

    return news_item_service.get_recent_headlines(channel_id, limit=4)


def _get_board_topics(site: Site, current_user: CurrentUser) -> List[DbTopic]:
    board_id = site.board_id
    if board_id is None:
        return []

    has_access = board_access_control_service.has_user_access_to_board(
        current_user.id, board_id
    )
    if not has_access:
        return []

    topics = board_topic_query_service.get_recent_topics(
        board_id, current_user, limit=6
    )

    board_helper_service.add_topic_unseen_flag(topics, current_user)

    return topics
