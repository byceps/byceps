"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from byceps.services.board import (
    category_command_service,
    posting_command_service,
    posting_query_service,
    topic_command_service,
    topic_query_service,
)
from byceps.services.board.dbmodels.posting import Posting as DbPosting
from byceps.services.board.dbmodels.topic import Topic as DbTopic
from byceps.services.board.transfer.models import (
    BoardID,
    Category,
    CategoryID,
    PostingID,
    TopicID,
)
from byceps.typing import UserID

from tests.helpers import generate_token


def create_category(
    board_id: BoardID,
    *,
    number: int = 1,
    slug: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Category:
    if slug is None:
        slug = generate_token()

    if title is None:
        title = generate_token()

    if description is None:
        description = f'Hier geht es um Kategorie {number}'

    return category_command_service.create_category(
        board_id, slug, title, description
    )


def create_topic(
    category_id: CategoryID,
    creator_id: UserID,
    *,
    number: int = 1,
    title: Optional[str] = None,
    body: Optional[str] = None,
) -> DbTopic:
    if title is None:
        title = f'Thema {number}'

    if body is None:
        body = f'Inhalt von Thema {number}'

    topic, _ = topic_command_service.create_topic(
        category_id, creator_id, title, body
    )

    return topic


def create_posting(
    topic_id: TopicID,
    creator_id: UserID,
    *,
    number: int = 1,
    body: Optional[str] = None,
) -> DbPosting:
    if body is None:
        body = f'Inhalt von Beitrag {number}.'

    posting, event = posting_command_service.create_posting(
        topic_id, creator_id, body
    )

    return posting


def find_topic(topic_id: TopicID) -> Optional[DbTopic]:
    return topic_query_service.find_topic_by_id(topic_id)


def find_posting(posting_id: PostingID) -> Optional[DbPosting]:
    return posting_query_service.find_posting_by_id(posting_id)
