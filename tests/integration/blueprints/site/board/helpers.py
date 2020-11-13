"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.board import (
    category_command_service,
    posting_command_service,
    posting_query_service,
    topic_command_service,
    topic_query_service,
)


def create_category(
    board_id, *, number=1, slug=None, title=None, description=None
):
    if slug is None:
        slug = f'category-{number}'

    if title is None:
        title = f'Kategorie {number}'

    if description is None:
        description = f'Hier geht es um Kategorie {number}'

    return category_command_service.create_category(
        board_id, slug, title, description
    )


def create_topic(category_id, creator_id, *, number=1, title=None, body=None):
    if title is None:
        title = f'Thema {number}'

    if body is None:
        body = f'Inhalt von Thema {number}'

    topic, _ = topic_command_service.create_topic(
        category_id, creator_id, title, body
    )

    return topic


def create_posting(topic_id, creator_id, *, number=1, body=None):
    if body is None:
        body = f'Inhalt von Beitrag {number}.'

    posting, event = posting_command_service.create_posting(
        topic_id, creator_id, body
    )

    return posting


def find_topic(topic_id):
    return topic_query_service.find_topic_by_id(topic_id)


def find_posting(posting_id):
    return posting_query_service.find_posting_by_id(posting_id)
