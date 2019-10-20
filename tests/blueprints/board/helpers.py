"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import (
    topic_query_service as board_topic_query_service,
)

from testfixtures.board import (
    create_board as _create_board,
    create_category as _create_category,
    create_topic as _create_topic,
)


def create_board(brand_id):
    board_id = brand_id
    return _create_board(brand_id, board_id)


def create_category(board_id, number):
    return _create_category(board_id, number=number)


def create_topic(category_id, creator_id, number):
    return _create_topic(category_id, creator_id, number=number)


def find_topic(topic_id):
    return board_topic_query_service.find_topic_by_id(topic_id)
