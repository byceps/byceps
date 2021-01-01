"""
byceps.blueprints.site.board._helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, url_for

from ....services.board import (
    access_control_service,
    category_query_service as board_category_query_service,
    posting_query_service as board_posting_query_service,
    topic_query_service as board_topic_query_service,
)
from ....services.site import service as site_service


def get_board_id():
    site = site_service.get_site(g.site_id)

    board_id = site.board_id
    if board_id is None:
        abort(404)

    return board_id


def get_category_or_404(category_id):
    category = board_category_query_service.find_category_by_id(category_id)

    if category is None:
        abort(404)

    board_id = get_board_id()

    if category.board_id != board_id:
        abort(404)

    require_board_access(board_id, g.current_user.id)

    return category


def get_topic_or_404(topic_id):
    topic = board_topic_query_service.find_topic_by_id(topic_id)

    if topic is None:
        abort(404)

    board_id = get_board_id()

    if topic.category.board_id != board_id:
        abort(404)

    require_board_access(board_id, g.current_user.id)

    return topic


def get_posting_or_404(posting_id):
    posting = board_posting_query_service.find_posting_by_id(posting_id)

    if posting is None:
        abort(404)

    board_id = get_board_id()

    if posting.topic.category.board_id != board_id:
        abort(404)

    require_board_access(board_id, g.current_user.id)

    return posting


def require_board_access(board_id, user_id):
    has_access = access_control_service.has_user_access_to_board(
        user_id, board_id
    )
    if not has_access:
        abort(404)


def build_external_url_for_topic(topic_id):
    return build_url_for_topic(topic_id, external=True)


def build_url_for_topic(topic_id, *, external=False):
    return url_for('board.topic_view', topic_id=topic_id, _external=external)


def build_url_for_topic_in_category_view(topic):
    return url_for(
        'board.category_view',
        slug=topic.category.slug,
        _anchor=f'topic-{topic.id}',
    )


def build_external_url_for_posting(posting_id):
    return build_url_for_posting(posting_id, external=True)


def build_url_for_posting(posting_id, *, external=False):
    return url_for(
        'board.posting_view', posting_id=posting_id, _external=external
    )


def build_url_for_posting_in_topic_view(posting, page, **kwargs):
    return url_for(
        'board.topic_view',
        topic_id=posting.topic.id,
        page=page,
        _anchor=f'posting-{posting.id}',
        **kwargs,
    )
