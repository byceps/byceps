"""
byceps.services.board.posting_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional, Set

from ...database import db, Pagination
from ...typing import PartyID, UserID
from ...util.iterables import index_of

from ..authentication.session.models.current_user import CurrentUser
from ..user import service as user_service
from ..user.transfer.models import User

from .models.category import Category as DbCategory
from .models.posting import Posting as DbPosting
from .models.topic import Topic as DbTopic
from .transfer.models import BoardID, PostingID, TopicID


def count_postings_for_board(board_id: BoardID) -> int:
    """Return the number of postings for that board."""
    return DbPosting.query \
        .join(DbTopic).join(DbCategory).filter(DbCategory.board_id == board_id) \
        .count()


def find_posting_by_id(posting_id: PostingID) -> Optional[DbPosting]:
    """Return the posting with that id, or `None` if not found."""
    return DbPosting.query.get(posting_id)


def get_posting(posting_id: PostingID) -> DbPosting:
    """Return the posting with that id."""
    posting = find_posting_by_id(posting_id)

    if posting is None:
        raise ValueError(f'Unknown posting ID "{posting_id}"')

    return posting


def paginate_postings(
    topic_id: TopicID,
    user: CurrentUser,
    party_id: Optional[PartyID],
    page: int,
    postings_per_page: int,
) -> Pagination:
    """Paginate postings in that topic, as visible for the user."""
    postings = DbPosting.query \
        .options(
            db.joinedload(DbPosting.topic),
            db.joinedload(DbPosting.last_edited_by).load_only('screen_name'),
            db.joinedload(DbPosting.hidden_by).load_only('screen_name'),
        ) \
        .for_topic(topic_id) \
        .only_visible_for_user(user) \
        .earliest_to_latest() \
        .paginate(page, postings_per_page)

    creator_ids = {posting.creator_id for posting in postings.items}
    creators_by_id = _get_users_by_id(creator_ids, party_id)

    for posting in postings.items:
        posting.creator = creators_by_id[posting.creator_id]

    return postings


def _get_users_by_id(
    user_ids: Set[UserID], party_id: Optional[PartyID]
) -> Dict[UserID, User]:
    users = user_service.find_users(
        user_ids, include_avatars=True, include_orga_flags_for_party_id=party_id
    )
    return user_service.index_users_by_id(users)


def calculate_posting_page_number(
    posting: DbPosting, user: CurrentUser, postings_per_page: int
) -> int:
    """Return the number of the page the posting should appear on when
    viewed by the user.
    """
    topic_postings = DbPosting.query \
        .for_topic(posting.topic_id) \
        .only_visible_for_user(user) \
        .earliest_to_latest() \
        .all()

    index = index_of(lambda p: p == posting, topic_postings)
    if index is None:
        return 1  # Shouldn't happen.

    return divmod(index, postings_per_page)[0] + 1
