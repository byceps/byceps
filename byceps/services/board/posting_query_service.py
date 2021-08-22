"""
byceps.services.board.posting_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db, Pagination
from ...typing import UserID
from ...util.iterables import index_of

from ..user import service as user_service
from ..user.transfer.models import User

from .dbmodels.category import Category as DbCategory
from .dbmodels.posting import Posting as DbPosting
from .dbmodels.topic import Topic as DbTopic
from .transfer.models import BoardID, PostingID, TopicID


def count_postings_for_board(board_id: BoardID) -> int:
    """Return the number of postings for that board."""
    return db.session \
        .query(DbPosting) \
        .join(DbTopic).join(DbCategory).filter(DbCategory.board_id == board_id) \
        .count()


def find_posting_by_id(posting_id: PostingID) -> Optional[DbPosting]:
    """Return the posting with that id, or `None` if not found."""
    return db.session.query(DbPosting).get(posting_id)


def get_posting(posting_id: PostingID) -> DbPosting:
    """Return the posting with that id."""
    posting = find_posting_by_id(posting_id)

    if posting is None:
        raise ValueError(f'Unknown posting ID "{posting_id}"')

    return posting


def paginate_postings(
    topic_id: TopicID,
    include_hidden: bool,
    page: int,
    postings_per_page: int,
) -> Pagination:
    """Paginate postings in that topic, as visible for the user."""
    query = db.session \
        .query(DbPosting) \
        .options(
            db.joinedload(DbPosting.topic),
            db.joinedload(DbPosting.last_edited_by).load_only('screen_name'),
            db.joinedload(DbPosting.hidden_by).load_only('screen_name'),
        ) \
        .filter_by(topic_id=topic_id)

    if not include_hidden:
        query = query.filter_by(hidden=False)

    postings = query \
        .order_by(DbPosting.created_at.asc()) \
        .paginate(page, postings_per_page)

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
    query = db.session \
        .query(DbPosting) \
        .filter_by(topic_id=posting.topic_id)

    if not include_hidden:
        query = query.filter_by(hidden=False)

    topic_postings = query \
        .order_by(DbPosting.created_at.asc()) \
        .all()

    index = index_of(topic_postings, lambda p: p == posting)
    if index is None:
        return 1  # Shouldn't happen.

    return divmod(index, postings_per_page)[0] + 1
