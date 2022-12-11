"""
byceps.services.board.dbmodels.posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.dbmodels.user import DbUser

from .topic import DbTopic


class DbPosting(db.Model):
    """A posting."""

    __tablename__ = 'board_postings'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    topic_id = db.Column(
        db.Uuid, db.ForeignKey('board_topics.id'), index=True, nullable=False
    )
    topic = db.relationship(DbTopic, backref='postings')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.UnicodeText, nullable=False)
    last_edited_at = db.Column(db.DateTime)
    last_edited_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_edited_by = db.relationship(DbUser, foreign_keys=[last_edited_by_id])
    edit_count = db.Column(db.Integer, default=0, nullable=False)
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(DbUser, foreign_keys=[hidden_by_id])

    def __init__(self, topic: DbTopic, creator_id: UserID, body: str) -> None:
        self.topic = topic
        self.creator_id = creator_id
        self.body = body

    def is_initial_topic_posting(self, topic: DbTopic) -> bool:
        return self == topic.initial_posting

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        builder = (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('topic', self.topic.title)
        )

        if self.hidden:
            builder.add_custom(f'hidden by {self.hidden_by.screen_name}')

        return builder.build()


class DbInitialTopicPostingAssociation(db.Model):
    __tablename__ = 'board_initial_topic_postings'

    topic_id = db.Column(
        db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True
    )
    topic = db.relationship(
        DbTopic,
        backref=db.backref('initial_topic_posting_association', uselist=False),
    )
    posting_id = db.Column(
        db.Uuid, db.ForeignKey('board_postings.id'), unique=True, nullable=False
    )
    posting = db.relationship(DbPosting)

    def __init__(self, topic: DbTopic, posting: DbPosting) -> None:
        self.topic = topic
        self.posting = posting
