"""
byceps.services.board.blueprints.site._helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, url_for

from byceps.services.board import (
    board_access_control_service,
    board_category_query_service,
    board_posting_query_service,
    board_topic_query_service,
)


def get_board_id():
    board_id = g.site.board_id
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

    require_board_access(board_id, g.user.id)

    return category


def get_db_topic_or_404(topic_id):
    db_topic = board_topic_query_service.find_db_topic(topic_id)

    if db_topic is None:
        abort(404)

    board_id = get_board_id()

    if db_topic.category.board_id != board_id:
        abort(404)

    require_board_access(board_id, g.user.id)

    return db_topic


def get_db_posting_or_404(posting_id):
    db_posting = board_posting_query_service.find_db_posting(posting_id)

    if db_posting is None:
        abort(404)

    board_id = get_board_id()

    if db_posting.topic.category.board_id != board_id:
        abort(404)

    require_board_access(board_id, g.user.id)

    return db_posting


def require_board_access(board_id, user_id):
    has_access = board_access_control_service.has_user_access_to_board(
        user_id, board_id
    )
    if not has_access:
        abort(404)


def build_external_url_for_topic(topic_id):
    return build_url_for_topic(topic_id, external=True)


def build_url_for_topic(topic_id, *, external=False):
    return url_for('board.topic_view', topic_id=topic_id, _external=external)


def build_url_for_topic_in_category_view(db_topic):
    return url_for(
        'board.category_view',
        slug=db_topic.category.slug,
        _anchor=f'topic-{db_topic.id}',
    )


def build_external_url_for_posting(posting_id):
    return build_url_for_posting(posting_id, external=True)


def build_url_for_posting(posting_id, *, external=False):
    return url_for(
        'board.posting_view', posting_id=posting_id, _external=external
    )


def build_url_for_posting_in_topic_view(db_posting, page, **kwargs):
    return url_for(
        'board.topic_view',
        topic_id=db_posting.topic.id,
        page=page,
        _anchor=f'posting-{db_posting.id}',
        **kwargs,
    )
