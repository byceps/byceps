"""
byceps.services.board.board_aggregation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.models.user import UserID

from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbPosting
from .dbmodels.topic import DbTopic
from .models import BoardCategoryID, TopicID


@dataclass(frozen=True, kw_only=True)
class LatestPostingInfo:
    created_at: datetime
    creator_id: UserID


def aggregate_category(db_category: DbBoardCategory) -> None:
    """Update the category's count and latest fields."""
    topic_count = _get_category_topic_count(db_category.id)
    posting_count = _get_category_posting_count(db_category.id)
    latest_posting_info = _get_category_latest_posting_info(db_category.id)

    db_category.topic_count = topic_count
    db_category.posting_count = posting_count
    db_category.last_posting_updated_at = (
        latest_posting_info.created_at if latest_posting_info else None
    )
    db_category.last_posting_updated_by_id = (
        latest_posting_info.creator_id if latest_posting_info else None
    )

    db.session.commit()


def _get_category_topic_count(category_id: BoardCategoryID) -> int:
    topic_count = db.session.scalar(
        select(db.func.count(DbTopic.id))
        .filter_by(category_id=category_id)
        .filter_by(hidden=False)
    )
    return topic_count or 0


def _get_category_posting_count(category_id: BoardCategoryID) -> int:
    posting_count = db.session.scalar(
        select(db.func.count(DbPosting.id))
        .filter(DbPosting.hidden == False)  # noqa: E712
        .join(DbTopic)
        .filter(DbTopic.category_id == category_id)
        .filter(DbTopic.hidden == False)  # noqa: E712
    )
    return posting_count or 0


def _get_category_latest_posting_info(
    category_id: BoardCategoryID,
) -> LatestPostingInfo | None:
    db_latest_posting = db.session.scalars(
        select(DbPosting)
        .filter(DbPosting.hidden == False)  # noqa: E712
        .join(DbTopic)
        .filter(DbTopic.category_id == category_id)
        .filter(DbTopic.hidden == False)  # noqa: E712
        .order_by(DbPosting.created_at.desc())
    ).first()

    if not db_latest_posting:
        return None

    return LatestPostingInfo(
        created_at=db_latest_posting.created_at,
        creator_id=db_latest_posting.creator_id,
    )


def aggregate_topic(db_topic: DbTopic) -> None:
    """Update the topic's count and latest fields."""
    posting_count = _get_topic_posting_count(db_topic.id)
    latest_posting_info = _get_topic_latest_posting_info(db_topic.id)

    db_topic.posting_count = posting_count
    db_topic.last_updated_at = (
        latest_posting_info.created_at if latest_posting_info else None
    )
    db_topic.last_updated_by_id = (
        latest_posting_info.creator_id if latest_posting_info else None
    )

    db.session.commit()

    aggregate_category(db_topic.category)


def _get_topic_posting_count(topic_id: TopicID) -> int:
    posting_count = db.session.scalar(
        select(db.func.count(DbPosting.id))
        .filter_by(topic_id=topic_id)
        .filter_by(hidden=False)
    )
    return posting_count or 0


def _get_topic_latest_posting_info(
    topic_id: TopicID,
) -> LatestPostingInfo | None:
    db_latest_posting = db.session.scalars(
        select(DbPosting)
        .filter_by(topic_id=topic_id)
        .filter_by(hidden=False)
        .order_by(DbPosting.created_at.desc())
    ).first()

    if not db_latest_posting:
        return None

    return LatestPostingInfo(
        created_at=db_latest_posting.created_at,
        creator_id=db_latest_posting.creator_id,
    )
