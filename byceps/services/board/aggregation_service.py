"""
byceps.services.board.aggregation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db

from .dbmodels.category import Category as DbCategory
from .dbmodels.posting import Posting as DbPosting
from .dbmodels.topic import Topic as DbTopic


def aggregate_category(category: DbCategory) -> None:
    """Update the category's count and latest fields."""
    topic_count = DbTopic.query \
        .filter_by(category_id=category.id) \
        .filter_by(hidden=False) \
        .count()

    posting_query = DbPosting.query \
        .filter(DbPosting.hidden == False) \
        .join(DbTopic) \
            .filter(DbTopic.category_id == category.id)

    posting_count = posting_query.count()

    latest_posting = posting_query \
        .filter(DbTopic.hidden == False) \
        .order_by(DbPosting.created_at.desc()) \
        .first()

    category.topic_count = topic_count
    category.posting_count = posting_count
    category.last_posting_updated_at = latest_posting.created_at \
                                        if latest_posting else None
    category.last_posting_updated_by_id = latest_posting.creator_id \
                                        if latest_posting else None

    db.session.commit()


def aggregate_topic(topic: DbTopic) -> None:
    """Update the topic's count and latest fields."""
    posting_query = DbPosting.query \
        .filter_by(topic_id=topic.id) \
        .filter_by(hidden=False)

    posting_count = posting_query.count()

    latest_posting = posting_query \
        .order_by(DbPosting.created_at.desc()) \
        .first()

    topic.posting_count = posting_count
    if latest_posting:
        topic.last_updated_at = latest_posting.created_at
        topic.last_updated_by_id = latest_posting.creator_id

    db.session.commit()

    aggregate_category(topic.category)
