"""
byceps.services.board.posting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import UserID
from ...util.iterables import index_of

from ..user.models.user import User

from .aggregation_service import aggregate_topic
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


def paginate_postings(topic_id: TopicID, user: User, page: int,
                      postings_per_page: int) -> Pagination:
    """Paginate postings in that topic, as visible for the user."""
    return DbPosting.query \
        .options(
            db.joinedload(DbPosting.topic),
            db.joinedload('creator')
                .load_only('id', 'screen_name')
                .joinedload('orga_team_memberships'),
            db.joinedload(DbPosting.last_edited_by).load_only('screen_name'),
            db.joinedload(DbPosting.hidden_by).load_only('screen_name'),
        ) \
        .for_topic(topic_id) \
        .only_visible_for_user(user) \
        .earliest_to_latest() \
        .paginate(page, postings_per_page)


def create_posting(topic: DbTopic, creator_id: UserID, body: str) -> DbPosting:
    """Create a posting in that topic."""
    posting = DbPosting(topic, creator_id, body)
    db.session.add(posting)
    db.session.commit()

    aggregate_topic(topic)

    return posting


def update_posting(posting: DbPosting, editor_id: UserID, body: str, *,
                   commit: bool=True) -> None:
    """Update the posting."""
    posting.body = body.strip()
    posting.last_edited_at = datetime.now()
    posting.last_edited_by_id = editor_id
    posting.edit_count += 1

    if commit:
        db.session.commit()


def calculate_posting_page_number(posting: DbPosting, user: User,
                                  postings_per_page: int) -> int:
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


def hide_posting(posting: DbPosting, hidden_by_id: UserID) -> None:
    """Hide the posting."""
    posting.hidden = True
    posting.hidden_at = datetime.now()
    posting.hidden_by_id = hidden_by_id
    db.session.commit()

    aggregate_topic(posting.topic)


def unhide_posting(posting: DbPosting, unhidden_by_id: UserID) -> None:
    """Un-hide the posting."""
    # TODO: Store who un-hid the posting.
    posting.hidden = False
    posting.hidden_at = None
    posting.hidden_by_id = None
    db.session.commit()

    aggregate_topic(posting.topic)
