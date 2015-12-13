# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import db

from .models.category import Category, LastCategoryView
from .models.posting import Posting
from .models.topic import LastTopicView, Topic


# -------------------------------------------------------------------- #
# category


def create_category(brand, position, slug, title, description):
    """Create a category in that brand's board."""
    category = Category(brand, position, slug, title, description)

    db.session.add(category)
    db.session.commit()

    return category


def aggregate_category(category):
    """Update the category's count and latest fields."""
    topic_count = Topic.query.for_category(category).without_hidden().count()

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
    category.last_posting_updated_by = latest_posting.creator \
                                        if latest_posting else None

    db.session.commit()


# -------------------------------------------------------------------- #
# topic


def create_topic(category, creator, title, body):
    """Create a topic with an initial posting in that category."""
    topic = Topic(category, creator, title)
    posting = Posting(topic, creator, body)

    db.session.add(topic)
    db.session.add(posting)
    db.session.commit()

    aggregate_topic(topic)

    return topic


def update_topic(topic, editor, title, body):
    """Update the topic (and its initial posting)."""
    topic.title = title.strip()

    posting = get_initial_posting_for_topic(topic)
    update_posting(posting, editor, body, commit=False)

    db.session.commit()


def aggregate_topic(topic):
    """Update the topic's count and latest fields."""
    posting_query = Posting.query.for_topic(topic).without_hidden()

    posting_count = posting_query.count()

    latest_posting = posting_query.latest_to_earliest().first()

    topic.posting_count = posting_count
    if latest_posting:
        topic.last_updated_at = latest_posting.created_at
        topic.last_updated_by = latest_posting.creator

    db.session.commit()

    aggregate_category(topic.category)


def get_initial_posting_for_topic(topic):
    """Return the initial posting of this topic."""
    return Posting.query \
        .filter_by(topic=topic) \
        .earliest_to_latest() \
        .first()


def find_default_posting_to_jump_to(topic, user, last_viewed_at):
    """Return the posting of the topic to show by default, or `None`."""
    if user.is_anonymous:
        # All postings are potentially new to a guest, so start on
        # the first page.
        return None

    if last_viewed_at is None:
        # This topic is completely new to the current user, so
        # start on the first page.
        return None

    first_new_posting_query = Posting.query \
        .for_topic(topic) \
        .only_visible_for_current_user() \
        .earliest_to_latest()

    first_new_posting = first_new_posting_query \
        .filter(Posting.created_at > last_viewed_at) \
        .first()

    if first_new_posting is None:
        # Current user has seen all postings so far, so show the last one.
        return first_new_posting_query.first()

    return first_new_posting


# -------------------------------------------------------------------- #
# posting


def create_posting(topic, creator, body):
    """Create a posting in that topic."""
    posting = Posting(topic, creator, body)
    db.session.add(posting)
    db.session.commit()

    aggregate_topic(topic)

    return posting


def update_posting(posting, editor, body, *, commit=True):
    """Update the posting."""
    posting.body = body.strip()
    posting.last_edited_at = datetime.now()
    posting.last_edited_by = editor
    posting.edit_count += 1

    if commit:
        db.session.commit()


# -------------------------------------------------------------------- #
# last views


def mark_category_as_just_viewed(category, user):
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    if user.is_anonymous:
        return

    last_view = LastCategoryView.find(user, category)
    if last_view is None:
        last_view = LastCategoryView(user, category)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()


def mark_topic_as_just_viewed(topic, user):
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    if user.is_anonymous:
        return

    last_view = LastTopicView.find(user, topic)
    if last_view is None:
        last_view = LastTopicView(user, topic)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()
