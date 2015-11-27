# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app, g, url_for

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder
from ...util.iterables import index_of

from ..brand.models import Brand
from ..user.models import User

from .authorization import BoardPostingPermission, BoardTopicPermission


class CategoryQuery(BaseQuery):

    def for_current_brand(self):
        return self.filter_by(brand=g.party.brand)


class Category(db.Model):
    """A category for topics."""
    __tablename__ = 'board_categories'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'position'),
        db.UniqueConstraint('brand_id', 'slug'),
        db.UniqueConstraint('brand_id', 'title'),
    )
    query_class = CategoryQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    brand = db.relationship(Brand)
    position = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.Unicode(40), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    description = db.Column(db.Unicode(80))
    topic_count = db.Column(db.Integer, default=0, nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    last_posting_updated_at = db.Column(db.DateTime)
    last_posting_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_posting_updated_by = db.relationship(User)

    def __init__(self, brand, position, slug, title, description):
        self.brand = brand
        self.position = position
        self.slug = slug
        self.title = title
        self.description = description

    def contains_unseen_postings(self):
        """Return `True` if the category contains postings created after
        the last time the current user viewed it.
        """
        # Don't display as new to a guest.
        if g.current_user.is_anonymous:
            return False

        if self.last_posting_updated_at is None:
            return False

        last_view = LastCategoryView.find(g.current_user, self)

        if last_view is None:
            return True

        return self.last_posting_updated_at > last_view.occured_at

    def mark_as_viewed(self):
        LastCategoryView.update(g.current_user, self)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('brand') \
            .add_with_lookup('slug') \
            .add_with_lookup('title') \
            .build()


class TopicQuery(BaseQuery):

    def for_category(self, category):
        return self.filter_by(category=category)

    def only_visible_for_current_user(self):
        """Only return topics the current user may see."""
        if not g.current_user.has_permission(BoardTopicPermission.view_hidden):
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

    def get_default_posting_to_jump_to(self, last_viewed_at):
        """Return the posting to show by default."""
        if g.current_user.is_anonymous:
            # All postings are potentially new to a guest, so start on
            # the first page.
            return None

        if last_viewed_at is None:
            # This topic is completely new to the current user, so
            # start on the first page.
            return None

        first_new_posting_query = Posting.query \
            .for_topic(self) \
            .only_visible_for_current_user() \
            .earliest_to_latest()

        first_new_posting = first_new_posting_query \
            .filter(Posting.created_at > last_viewed_at) \
            .first()

        if first_new_posting is None:
            # Current user has seen all postings so far, so show the last one.
            return first_new_posting_query.first()

        return first_new_posting

    @property
    def anchor(self):
        """Return the URL anchor for this topic."""
        return 'topic-{}'.format(self.id)

    @property
    def external_url(self):
        """Return the absolute URL of this topic."""
        return url_for('board.topic_view', id=self.id, _external=True)

    def get_body_posting(self):
        """Return the posting that stores the body of this topic's
        opening posting.
        """
        if not hasattr(self, '_body_posting'):
            self._body_posting = Posting.query \
                .filter_by(topic=self) \
                .earliest_to_latest() \
                .first()

        return self._body_posting

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

    def mark_as_viewed(self):
        LastTopicView.update(g.current_user, self)

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


class PostingQuery(BaseQuery):

    def for_topic(self, topic):
        return self.filter_by(topic=topic)

    def only_visible_for_current_user(self):
        """Only return postings the current user may see."""
        if not g.current_user.has_permission(BoardPostingPermission.view_hidden):
            return self.without_hidden()

        return self

    def without_hidden(self):
        """Only return postings every user may see."""
        return self.filter(Posting.hidden == False)

    def earliest_to_latest(self):
        return self.order_by(Posting.created_at.asc())

    def latest_to_earliest(self):
        return self.order_by(Posting.created_at.desc())


class Posting(db.Model):
    """A posting."""
    __tablename__ = 'board_postings'
    query_class = PostingQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'), index=True, nullable=False)
    topic = db.relationship(Topic, backref='postings')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User, foreign_keys=[creator_id])
    body = db.Column(db.UnicodeText, nullable=False)
    last_edited_at = db.Column(db.DateTime)
    last_edited_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_edited_by = db.relationship(User, foreign_keys=[last_edited_by_id])
    edit_count = db.Column(db.Integer, default=0, nullable=False)
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(User, foreign_keys=[hidden_by_id])

    def __init__(self, topic, creator, body):
        self.topic = topic
        self.creator = creator
        self.body = body

    def may_be_updated_by_user(self, user):
        return not self.topic.locked and (
            (
                user == self.creator and \
                user.has_permission(BoardPostingPermission.update)
            ) or \
            user.has_permission(BoardPostingPermission.update_of_others)
        )

    def hide(self, user):
        self.hidden = True
        self.hidden_at = datetime.now()
        self.hidden_by = user

    def unhide(self):
        self.hidden = False
        self.hidden_at = None
        self.hidden_by = None

    def calculate_page_number(self):
        """Return the number of the page this posting should appear on."""
        topic_postings = Posting.query \
            .for_topic(self.topic) \
            .only_visible_for_current_user() \
            .earliest_to_latest() \
            .all()

        index = index_of(lambda p: p == self, topic_postings)
        if index is None:
            return  # Shouldn't happen.

        per_page = int(current_app.config['BOARD_POSTINGS_PER_PAGE'])
        return divmod(index, per_page)[0] + 1

    @property
    def anchor(self):
        """Return the URL anchor for this posting."""
        return 'posting-{}'.format(self.id)

    @property
    def external_url(self):
        """Return the absolute URL of this posting (in its topic)."""
        return url_for('board.posting_view', id=self.id, _external=True)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('topic', self.topic.title) \
            .add('creator', self.creator.screen_name)

        if self.hidden:
            builder.add_custom('hidden by {}'.format(self.hidden_by.screen_name))

        return builder.build()


class LastCategoryView(db.Model):
    """The last time a user looked into specific category."""
    __tablename__ = 'board_categories_lastviews'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, foreign_keys=[user_id])
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'), primary_key=True)
    category = db.relationship(Category)
    occured_at = db.Column(db.DateTime, nullable=False)

    @classmethod
    def find(cls, user, category):
        if user.is_anonymous:
            return

        return cls.query.filter_by(user=user, category=category).first()

    @classmethod
    def update(cls, user, category):
        if user.is_anonymous:
            return

        last_view = cls.find(user, category)
        if last_view is None:
            last_view = cls(user=user, category=category)
            db.session.add(last_view)

        last_view.occured_at = datetime.now()
        db.session.commit()

    def __repr__(self):
        return ReprBuilder(self) \
            .add('user', self.user.screen_name) \
            .add('category', self.category.title) \
            .add_with_lookup('occured_at') \
            .build()


class LastTopicView(db.Model):
    """The last time a user looked into specific topic."""
    __tablename__ = 'board_topics_lastviews'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, foreign_keys=[user_id])
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True)
    topic = db.relationship(Topic)
    occured_at = db.Column(db.DateTime, nullable=False)

    @classmethod
    def find(cls, user, topic):
        if user.is_anonymous:
            return

        return cls.query.filter_by(user=user, topic=topic).first()

    @classmethod
    def update(cls, user, topic):
        if user.is_anonymous:
            return

        last_view = cls.find(user, topic)
        if last_view is None:
            last_view = cls(user=user, topic=topic)
            db.session.add(last_view)

        last_view.occured_at = datetime.now()
        db.session.commit()

    def __repr__(self):
        return ReprBuilder(self) \
            .add('user', self.user.screen_name) \
            .add('topic', self.topic.title) \
            .add_with_lookup('occured_at') \
            .build()
