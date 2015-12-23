# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models.posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import url_for

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder
from ....util.iterables import index_of

from ...user.models import User

from ..authorization import BoardPostingPermission

from .topic import Topic


class PostingQuery(BaseQuery):

    def for_topic(self, topic):
        return self.filter_by(topic=topic)

    def only_visible_for_user(self, user):
        """Only return postings the user may see."""
        if not user.has_permission(BoardPostingPermission.view_hidden):
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

    def is_initial_topic_posting(self, topic):
        return self == topic.initial_posting

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

    def is_unseen(self, user, last_viewed_at):
        # Don't display any posting as new to a guest.
        if user.is_anonymous:
            return False

        # Don't display the author's own posting as new to him/her.
        if self.creator == user:
            return False

        return (last_viewed_at is None) or (self.created_at > last_viewed_at)

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


class InitialTopicPostingAssociation(db.Model):
    __tablename__ = 'board_initial_topic_postings'

    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True)
    topic = db.relationship(Topic, backref=db.backref('initial_topic_posting_association', uselist=False))
    posting_id = db.Column(db.Uuid, db.ForeignKey('board_postings.id'), unique=True, nullable=False)
    posting = db.relationship(Posting)

    def __init__(self, topic, posting):
        self.topic = topic
        self.posting = posting
