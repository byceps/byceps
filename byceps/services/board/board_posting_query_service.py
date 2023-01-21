"""
byceps.services.board.board_posting_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import select

from ...database import db, paginate, Pagination
from ...typing import UserID
from ...util.iterables import index_of

from ..user.dbmodels.user import DbUser
from ..user.models.user import User
from ..user import user_service

from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbPosting
from .dbmodels.topic import DbTopic
from .models import BoardID, PostingID, TopicID


def count_postings_for_board(board_id: BoardID) -> int:
    """Return the number of postings for that board."""
    return db.session.scalar(
        select(db.func.count(DbPosting.id))
        .join(DbTopic)
        .join(DbBoardCategory)
        .filter(DbBoardCategory.board_id == board_id)
    )


def find_posting_by_id(posting_id: PostingID) -> Optional[DbPosting]:
    """Return the posting with that id, or `None` if not found."""
    return db.session.get(DbPosting, posting_id)


def get_posting(posting_id: PostingID) -> DbPosting:
    """Return the posting with that id."""
    db_posting = find_posting_by_id(posting_id)

    if db_posting is None:
        raise ValueError(f'Unknown posting ID "{posting_id}"')

    return db_posting


def paginate_postings(
    topic_id: TopicID,
    include_hidden: bool,
    page: int,
    per_page: int,
) -> Pagination:
    """Paginate postings in that topic, as visible for the user."""
    items_stmt = (
        select(DbPosting)
        .options(
            db.joinedload(DbPosting.topic),
            db.joinedload(DbPosting.last_edited_by).load_only(
                DbUser.screen_name
            ),
            db.joinedload(DbPosting.hidden_by).load_only(DbUser.screen_name),
        )
        .filter_by(topic_id=topic_id)
        .order_by(DbPosting.created_at.asc())
    )

    count_stmt = select(db.func.count(DbPosting.id)).filter_by(
        topic_id=topic_id
    )

    if not include_hidden:
        items_stmt = items_stmt.filter_by(hidden=False)
        count_stmt = count_stmt.filter_by(hidden=False)

    postings = paginate(items_stmt, count_stmt, page, per_page)

    creator_ids = {posting.creator_id for posting in postings.items}
    creators_by_id = _get_users_by_id(creator_ids)

    for posting in postings.items:
        posting.creator = creators_by_id[posting.creator_id]

    return postings


def _get_users_by_id(user_ids: set[UserID]) -> dict[UserID, User]:
    users = user_service.get_users(user_ids, include_avatars=True)
    return user_service.index_users_by_id(users)


def calculate_posting_page_number(
    posting: DbPosting, include_hidden: bool, postings_per_page: int
) -> int:
    """Return the number of the page the posting should appear on."""
    stmt = select(DbPosting).filter_by(topic_id=posting.topic_id)

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    stmt = stmt.order_by(DbPosting.created_at.asc())

    topic_postings = db.session.scalars(stmt).all()

    index = index_of(topic_postings, lambda p: p == posting)
    if index is None:
        return 1  # Shouldn't happen.

    return divmod(index, postings_per_page)[0] + 1
