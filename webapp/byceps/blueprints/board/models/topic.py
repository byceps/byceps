# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app, g, url_for
from sqlalchemy.ext.associationproxy import association_proxy

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...user.models import User

from ..authorization import BoardTopicPermission

from .category import Category


class TopicQuery(BaseQuery):

    def for_category(self, category):
        return self.filter_by(category=category)

    def only_visible_for_user(self, user):
        """Only return topics the user may see."""
        if not user.has_permission(BoardTopicPermission.view_hidden):
            return self.without_hidden()

        return self

    def without_hidden(self):
        """Only return topics every user may see."""
        return self.filter(Topic.hidden == False)

    def with_id_or_404(self, id):
        return self.filter_by(id=id).first_or_404()


class Topic(db.Model):
    """A topic."""
    __tablename__ = 'board_topics'
    query_class = TopicQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'), index=True, nullable=False)
    category = db.relationship(Category)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User, foreign_keys=[creator_id])
    title = db.Column(db.Unicode(80), nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    last_updated_at = db.Column(db.DateTime, default=datetime.now)
    last_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_updated_by = db.relationship(User, foreign_keys=[last_updated_by_id])
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(User, foreign_keys=[hidden_by_id])
    locked = db.Column(db.Boolean, default=False, nullable=False)
    locked_at = db.Column(db.DateTime)
    locked_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    locked_by = db.relationship(User, foreign_keys=[locked_by_id])
    pinned = db.Column(db.Boolean, default=False, nullable=False)
    pinned_at = db.Column(db.DateTime)
    pinned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    pinned_by = db.relationship(User, foreign_keys=[pinned_by_id])
    initial_posting = association_proxy('initial_topic_posting_association', 'posting')

    def __init__(self, category, creator, title):
        self.category = category
        self.creator = creator
        self.title = title

    def may_be_updated_by_user(self, user):
        return not self.locked and (
            (
                user == self.creator and \
                user.has_permission(BoardTopicPermission.update)
            ) or \
            user.has_permission(BoardTopicPermission.update_of_others)
        )

    def hide(self, user):
        self.hidden = True
        self.hidden_at = datetime.now()
        self.hidden_by = user

    def unhide(self):
        self.hidden = False
        self.hidden_at = None
        self.hidden_by = None

    def lock(self, user):
        self.locked = True
        self.locked_at = datetime.now()
        self.locked_by = user

    def unlock(self):
        self.locked = False
        self.locked_at = None
        self.locked_by = None

    def pin(self, user):
        self.pinned = True
        self.pinned_at = datetime.now()
        self.pinned_by = user

    def unpin(self):
        self.pinned = False
        self.pinned_at = None
        self.pinned_by = None

    @property
    def reply_count(self):
        return self.posting_count - 1

    @property
    def page_count(self):
        """Return the number of pages this topic spans."""
        postings_per_page = int(current_app.config['BOARD_POSTINGS_PER_PAGE'])
        full_page_count, remaining_postings = divmod(self.posting_count,
                                                     postings_per_page)
        if remaining_postings > 0:
            return full_page_count + 1
        else:
            return full_page_count

    @property
    def anchor(self):
        """Return the URL anchor for this topic."""
        return 'topic-{}'.format(self.id)

    @property
    def external_url(self):
        """Return the absolute URL of this topic."""
        return url_for('board.topic_view', id=self.id, _external=True)

    def contains_unseen_postings(self):
        """Return `True` if the topic contains postings created after
        the last time the current user viewed it.
        """
        # Don't display as new to a guest.
        if g.current_user.is_anonymous:
            return False

        last_viewed_at = self.last_viewed_at
        return last_viewed_at is None \
            or self.last_updated_at > last_viewed_at

    @property
    def last_viewed_at(self):
        last_view = LastTopicView.find(g.current_user, self)
        return last_view.occured_at if last_view is not None else None

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('category', self.category.title) \
            .add('creator', self.creator.screen_name) \
            .add_with_lookup('title')

        if self.hidden:
            builder.add_custom('hidden by {}'.format(self.hidden_by.screen_name))

        if self.locked:
            builder.add_custom('locked by {}'.format(self.locked_by.screen_name))

        if self.pinned:
            builder.add_custom('pinned by {}'.format(self.pinned_by.screen_name))

        return builder.build()


class LastTopicView(db.Model):
    """The last time a user looked into specific topic."""
    __tablename__ = 'board_topics_lastviews'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, foreign_keys=[user_id])
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True)
    topic = db.relationship(Topic)
    occured_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, topic):
        self.user = user
        self.topic = topic

    @classmethod
    def find(cls, user, topic):
        if user.is_anonymous:
            return

        return cls.query.filter_by(user=user, topic=topic).first()

    def __repr__(self):
        return ReprBuilder(self) \
            .add('user', self.user.screen_name) \
            .add('topic', self.topic.title) \
            .add_with_lookup('occured_at') \
            .build()
