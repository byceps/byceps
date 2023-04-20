"""
byceps.services.board.board_aggregation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db

from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbPosting
from .dbmodels.topic import DbTopic


def aggregate_category(db_category: DbBoardCategory) -> None:
    """Update the category's count and latest fields."""
    topic_count = db.session.scalar(
        select(db.func.count(DbTopic.id))
        .filter_by(category_id=db_category.id)
        .filter_by(hidden=False)
    )

    posting_count = db.session.scalar(
        select(db.func.count(DbPosting.id))
        .filter(DbPosting.hidden == False)  # noqa: E712
        .join(DbTopic)
        .filter(DbTopic.category_id == db_category.id)
    )

    db_latest_posting = db.session.scalars(
        select(DbPosting)
        .filter(DbPosting.hidden == False)  # noqa: E712
        .join(DbTopic)
        .filter(DbTopic.category_id == db_category.id)
        .filter(DbTopic.hidden == False)  # noqa: E712
        .order_by(DbPosting.created_at.desc())
    ).first()

    db_category.topic_count = topic_count
    db_category.posting_count = posting_count
    db_category.last_posting_updated_at = (
        db_latest_posting.created_at if db_latest_posting else None
    )
    db_category.last_posting_updated_by_id = (
        db_latest_posting.creator_id if db_latest_posting else None
    )

    db.session.commit()


def aggregate_topic(db_topic: DbTopic) -> None:
    """Update the topic's count and latest fields."""
    posting_count = db.session.scalar(
        select(db.func.count(DbPosting.id))
        .filter_by(topic_id=db_topic.id)
        .filter_by(hidden=False)
    )

    db_latest_posting = db.session.scalars(
        select(DbPosting)
        .filter_by(topic_id=db_topic.id)
        .filter_by(hidden=False)
        .order_by(DbPosting.created_at.desc())
    ).first()

    db_topic.posting_count = posting_count
    if db_latest_posting:
        db_topic.last_updated_at = db_latest_posting.created_at
        db_topic.last_updated_by_id = db_latest_posting.creator_id

    db.session.commit()

    aggregate_category(db_topic.category)
