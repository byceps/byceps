"""
byceps.services.board.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import BrandID, UserID
from ...util.iterables import index_of

from ..user.models.user import User

from .models.category import Category, LastCategoryView
from .models.posting import Posting, PostingID
from .models.topic import LastTopicView, Topic, TopicID
from . import topic_service


# -------------------------------------------------------------------- #
# posting


def count_postings_for_brand(brand_id: BrandID) -> int:
    """Return the number of postings for that brand."""
    return Posting.query \
        .join(Topic).join(Category).filter(Category.brand_id == brand_id) \
        .count()


def find_posting_by_id(posting_id: PostingID) -> Optional[Posting]:
    """Return the posting with that id, or `None` if not found."""
    return Posting.query.get(posting_id)


def paginate_postings(topic_id: TopicID, user: User, page: int,
                      postings_per_page: int) -> Pagination:
    """Paginate postings in that topic, as visible for the user."""
    return Posting.query \
        .options(
            db.joinedload(Posting.topic),
            db.joinedload('creator')
                .load_only('id', 'screen_name')
                .joinedload('orga_team_memberships'),
            db.joinedload(Posting.last_edited_by).load_only('screen_name'),
            db.joinedload(Posting.hidden_by).load_only('screen_name'),
        ) \
        .for_topic(topic_id) \
        .only_visible_for_user(user) \
        .earliest_to_latest() \
        .paginate(page, postings_per_page)


def create_posting(topic: Topic, creator_id: UserID, body: str) -> Posting:
    """Create a posting in that topic."""
    posting = Posting(topic, creator_id, body)
    db.session.add(posting)
    db.session.commit()

    topic_service.aggregate_topic(topic)

    return posting


def update_posting(posting: Posting, editor_id: UserID, body: str, *,
                   commit: bool=True) -> None:
    """Update the posting."""
    posting.body = body.strip()
    posting.last_edited_at = datetime.now()
    posting.last_edited_by_id = editor_id
    posting.edit_count += 1

    if commit:
        db.session.commit()


def calculate_posting_page_number(posting: Posting, user: User,
                                  postings_per_page: int) -> int:
    """Return the number of the page the posting should appear on when
    viewed by the user.
    """
    topic_postings = Posting.query \
        .for_topic(posting.topic_id) \
        .only_visible_for_user(user) \
        .earliest_to_latest() \
        .all()

    index = index_of(lambda p: p == posting, topic_postings)
    if index is None:
        return 1  # Shouldn't happen.

    return divmod(index, postings_per_page)[0] + 1


def hide_posting(posting: Posting, hidden_by_id: UserID) -> None:
    """Hide the posting."""
    posting.hidden = True
    posting.hidden_at = datetime.now()
    posting.hidden_by_id = hidden_by_id
    db.session.commit()

    topic_service.aggregate_topic(posting.topic)


def unhide_posting(posting: Posting, unhidden_by_id: UserID) -> None:
    """Un-hide the posting."""
    # TODO: Store who un-hid the posting.
    posting.hidden = False
    posting.hidden_at = None
    posting.hidden_by_id = None
    db.session.commit()

    topic_service.aggregate_topic(posting.topic)


# -------------------------------------------------------------------- #
# last views


def mark_category_as_just_viewed(category: Category, user: User) -> None:
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    if user.is_anonymous:
        return

    last_view = LastCategoryView.find(user, category)
    if last_view is None:
        last_view = LastCategoryView(user.id, category.id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()


def mark_topic_as_just_viewed(topic: Topic, user: User) -> None:
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    if user.is_anonymous:
        return

    last_view = LastTopicView.find(user, topic)
    if last_view is None:
        last_view = LastTopicView(user.id, topic.id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()
