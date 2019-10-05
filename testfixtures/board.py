"""
testfixtures.board
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import (
    board_service,
    category_command_service,
    posting_command_service,
    topic_command_service,
)


def create_board(brand_id, board_id):
    return board_service.create_board(brand_id, board_id)


def create_category(
    board_id, *, number=1, slug=None, title=None, description=None
):
    if slug is None:
        slug = 'category-{}'.format(number)

    if title is None:
        title = 'Kategorie {}'.format(number)

    if description is None:
        description = 'Hier geht es um Kategorie {}'.format(number)

    return category_command_service.create_category(
        board_id, slug, title, description
    )


def create_topic(category_id, creator_id, *, number=1, title=None, body=None):
    if title is None:
        title = 'Thema {}'.format(number)

    if body is None:
        body = 'Inhalt von Thema {}'.format(number)

    return topic_command_service.create_topic(
        category_id, creator_id, title, body
    )


def create_posting(topic, creator_id, *, number=1, body=None):
    if body is None:
        body = 'Inhalt von Beitrag {}.'.format(number)

    return posting_command_service.create_posting(topic, creator_id, body)
