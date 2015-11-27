# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import g

from ...database import db

from .models import Category, LastCategoryView, LastTopicView, Posting, Topic


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


def update_topic(topic, title, body):
    """Update the topic (and its initial posting)."""
    topic.title = title.strip()

    posting = topic.get_body_posting()
    posting.update(body, commit=False)

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


# -------------------------------------------------------------------- #
# posting


def create_posting(topic, creator, body):
    """Create a posting in that topic."""
    posting = Posting(topic, creator, body)
    db.session.add(posting)
    db.session.commit()

    aggregate_topic(topic)

    return posting


def update(posting, body, *, commit=True):
    """Update the posting."""
    posting.body = body.strip()
    posting.last_edited_at = datetime.now()
    posting.last_edited_by = g.current_user
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
