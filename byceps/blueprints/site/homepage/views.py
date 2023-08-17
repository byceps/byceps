"""
byceps.blueprints.site.homepage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Sequence

from flask import g

from byceps.blueprints.site.board import service as board_helper_service
from byceps.services.authentication.session.models import CurrentUser
from byceps.services.board import (
    board_access_control_service,
    board_topic_query_service,
)
from byceps.services.board.dbmodels.topic import DbTopic
from byceps.services.news import news_item_service
from byceps.services.news.models import NewsTeaser
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('homepage', __name__)


@blueprint.get('')
@templated
def index():
    """Show homepage."""
    news_teasers = _get_news_teasers()
    board_topics = _get_board_topics(g.user)

    return {
        'news_teasers': news_teasers,
        'board_topics': board_topics,
    }


def _get_news_teasers() -> list[NewsTeaser]:
    channel_ids = g.site.news_channel_ids
    if not channel_ids:
        return []

    return news_item_service.get_recent_teasers(channel_ids, limit=3)


def _get_board_topics(current_user: CurrentUser) -> Sequence[DbTopic]:
    board_id = g.site.board_id
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
