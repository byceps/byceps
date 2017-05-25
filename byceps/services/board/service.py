"""
byceps.services.board.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional, Sequence

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import BrandID, UserID
from ...util.iterables import index_of

from ..brand.models import Brand
from ..user.models.user import User

from .models.category import Category, CategoryID, LastCategoryView
from .models.posting import InitialTopicPostingAssociation, Posting, PostingID
from .models.topic import LastTopicView, Topic, TopicID


# -------------------------------------------------------------------- #
# category


def create_category(brand: Brand, slug: str, title: str, description: str
                   ) -> Category:
    """Create a category in that brand's board."""
    category = Category(brand.id, slug, title, description)
    brand.board_categories.append(category)

    db.session.commit()

    return category


def update_category(category: Category, slug: str, title: str, description: str
                   ) -> Category:
    """Update the category."""
    category.slug = slug.strip().lower()
    category.title = title.strip()
    category.description = description.strip()

    db.session.commit()

    return category


def move_category_up(category: Category) -> None:
    """Move a category upwards by one position."""
    category_list = category.brand.board_categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category: Category) -> None:
    """Move a category downwards by one position."""
    category_list = category.brand.board_categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()


def count_categories_for_brand(brand_id: BrandID) -> int:
    """Return the number of categories for that brand."""
    return Category.query.for_brand_id(brand_id).count()


def find_category_by_id(category_id: CategoryID) -> Optional[Category]:
    """Return the category with that id, or `None` if not found."""
    return Category.query.get(category_id)


def find_category_by_slug(brand_id: BrandID, slug: str) -> Optional[Category]:
    """Return the category for that brand and slug, or `None` if not found."""
    return Category.query \
        .for_brand_id(brand_id) \
        .filter_by(slug=slug) \
        .first()


def get_categories(brand_id: BrandID) -> Sequence[Category]:
    """Return all categories for that brand, ordered by position."""
    return Category.query \
        .for_brand_id(brand_id) \
        .order_by(Category.position) \
        .all()


def get_categories_excluding(brand_id: BrandID, category_id: CategoryID
                            ) -> Sequence[Category]:
    """Return all categories for that brand except for the specified one."""
    return Category.query \
        .for_brand_id(brand_id) \
        .filter(Category.id != category_id) \
        .order_by(Category.position) \
        .all()


def get_categories_with_last_updates(brand_id: BrandID) -> Sequence[Category]:
    """Return the categories for that brand.

    Include the creator of the last posting in each category.
    """
    return Category.query \
        .for_brand_id(brand_id) \
        .options(
            db.joinedload(Category.last_posting_updated_by),
        ) \
        .all()


def aggregate_category(category: Category) -> None:
    """Update the category's count and latest fields."""
    topic_count = Topic.query.for_category(category.id).without_hidden().count()

    posting_query = Posting.query \
        .without_hidden() \
        .join(Topic) \
            .filter_by(category=category)

    posting_count = posting_query.count()

    latest_posting = posting_query \
        .filter(Topic.hidden == False) \
        .latest_to_earliest() \
        .first()

    category.topic_count = topic_count
    category.posting_count = posting_count
    category.last_posting_updated_at = latest_posting.created_at \
                                        if latest_posting else None
    category.last_posting_updated_by_id = latest_posting.creator_id \
                                        if latest_posting else None

    db.session.commit()


# -------------------------------------------------------------------- #
# topic


def count_topics_for_brand(brand_id: BrandID) -> int:
    """Return the number of topics for that brand."""
    return Topic.query \
        .join(Category).filter(Category.brand_id == brand_id) \
        .count()


def find_topic_by_id(topic_id: TopicID) -> Optional[Topic]:
    """Return the topic with that id, or `None` if not found."""
    return Topic.query.get(topic_id)


def find_topic_visible_for_user(topic_id: TopicID, user: User
                               ) -> Optional[Topic]:
    """Return the topic with that id, or `None` if not found or
    invisible for the user.
    """
    return Topic.query \
        .options(
            db.joinedload(Topic.category),
        ) \
        .only_visible_for_user(user) \
        .filter_by(id=topic_id) \
        .first()


def paginate_topics(category_id: CategoryID, user: User, page: int,
                    topics_per_page: int) -> Pagination:
    """Paginate topics in that category, as visible for the user.

    Pinned topics are returned first.
    """
    return Topic.query \
        .for_category(category_id) \
        .options(
            db.joinedload(Topic.category),
            db.joinedload(Topic.creator),
            db.joinedload(Topic.last_updated_by),
            db.joinedload(Topic.hidden_by),
            db.joinedload(Topic.locked_by),
            db.joinedload(Topic.pinned_by),
        ) \
        .only_visible_for_user(user) \
        .order_by(Topic.pinned.desc(), Topic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)


def create_topic(category: Category, creator_id: UserID, title: str, body: str
                ) -> Topic:
    """Create a topic with an initial posting in that category."""
    topic = Topic(category.id, creator_id, title)
    posting = Posting(topic, creator_id, body)
    initial_topic_posting_association = InitialTopicPostingAssociation(topic,
                                                                       posting)

    db.session.add(topic)
    db.session.add(posting)
    db.session.add(initial_topic_posting_association)
    db.session.commit()

    _aggregate_topic(topic)

    return topic


def update_topic(topic: Topic, editor_id: UserID, title: str, body: str
                ) -> None:
    """Update the topic (and its initial posting)."""
    topic.title = title.strip()

    update_posting(topic.initial_posting, editor_id, body, commit=False)

    db.session.commit()


def _aggregate_topic(topic: Topic) -> None:
    """Update the topic's count and latest fields."""
    posting_query = Posting.query.for_topic(topic).without_hidden()

    posting_count = posting_query.count()

    latest_posting = posting_query.latest_to_earliest().first()

    topic.posting_count = posting_count
    if latest_posting:
        topic.last_updated_at = latest_posting.created_at
        topic.last_updated_by_id = latest_posting.creator_id

    db.session.commit()

    aggregate_category(topic.category)


def find_default_posting_to_jump_to(topic: Topic, user: User,
                                    last_viewed_at: Optional[datetime]
                                   ) -> Optional[Posting]:
    """Return the posting of the topic to show by default, or `None`."""
    if user.is_anonymous:
        # All postings are potentially new to a guest, so start on
        # the first page.
        return None

    if last_viewed_at is None:
        # This topic is completely new to the current user, so
        # start on the first page.
        return None

    postings_query = Posting.query \
        .for_topic(topic) \
        .only_visible_for_user(user)

    first_new_posting = postings_query \
        .filter(Posting.created_at > last_viewed_at) \
        .earliest_to_latest() \
        .first()

    if first_new_posting is None:
        # Current user has seen all postings so far, so show the last one.
        return postings_query \
            .latest_to_earliest() \
            .first()

    return first_new_posting


def hide_topic(topic: Topic, hidden_by_id: UserID) -> None:
    """Hide the topic."""
    topic.hidden = True
    topic.hidden_at = datetime.now()
    topic.hidden_by_id = hidden_by_id
    db.session.commit()

    _aggregate_topic(topic)


def unhide_topic(topic: Topic, unhidden_by_id: UserID) -> None:
    """Un-hide the topic."""
    # TODO: Store who un-hid the topic.
    topic.hidden = False
    topic.hidden_at = None
    topic.hidden_by_id = None
    db.session.commit()

    _aggregate_topic(topic)


def lock_topic(topic: Topic, locked_by_id: UserID) -> None:
    """Lock the topic."""
    topic.locked = True
    topic.locked_at = datetime.now()
    topic.locked_by_id = locked_by_id
    db.session.commit()


def unlock_topic(topic: Topic, unlocked_by_id: UserID) -> None:
    """Unlock the topic."""
    # TODO: Store who unlocked the topic.
    topic.locked = False
    topic.locked_at = None
    topic.locked_by_id = None
    db.session.commit()


def pin_topic(topic: Topic, pinned_by_id: UserID) -> None:
    """Pin the topic."""
    topic.pinned = True
    topic.pinned_at = datetime.now()
    topic.pinned_by_id = pinned_by_id
    db.session.commit()


def unpin_topic(topic: Topic, unpinned_by_id: UserID) -> None:
    """Unpin the topic."""
    # TODO: Store who unpinned the topic.
    topic.pinned = False
    topic.pinned_at = None
    topic.pinned_by_id = None
    db.session.commit()


def move_topic(topic: Topic, new_category: Category) -> None:
    """Move the topic to another category."""
    old_category = topic.category

    topic.category = new_category
    db.session.commit()

    for category in old_category, new_category:
        aggregate_category(category)


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


def paginate_postings(topic: Topic, user: User, page: int,
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
        .for_topic(topic) \
        .only_visible_for_user(user) \
        .earliest_to_latest() \
        .paginate(page, postings_per_page)


def create_posting(topic: Topic, creator_id: UserID, body: str) -> Posting:
    """Create a posting in that topic."""
    posting = Posting(topic, creator_id, body)
    db.session.add(posting)
    db.session.commit()

    _aggregate_topic(topic)

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
        .for_topic(posting.topic) \
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

    _aggregate_topic(posting.topic)


def unhide_posting(posting: Posting, unhidden_by_id: UserID) -> None:
    """Un-hide the posting."""
    # TODO: Store who un-hid the posting.
    posting.hidden = False
    posting.hidden_at = None
    posting.hidden_by_id = None
    db.session.commit()

    _aggregate_topic(posting.topic)


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
