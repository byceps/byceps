"""
byceps.services.board.dbmodels.posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import PostingID, TopicID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .topic import DbTopic


class DbPosting(db.Model):
    """A posting."""

    __tablename__ = 'board_postings'

    id: Mapped[PostingID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    topic_id: Mapped[TopicID] = mapped_column(
        db.Uuid, db.ForeignKey('board_topics.id'), index=True
    )
    topic: Mapped[DbTopic] = relationship(DbTopic, backref='postings')
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    body: Mapped[str] = mapped_column(db.UnicodeText)
    last_edited_at: Mapped[Optional[datetime]]
    last_edited_by_id: Mapped[Optional[UserID]] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    last_edited_by: Mapped[Optional[DbUser]] = relationship(
        DbUser, foreign_keys=[last_edited_by_id]
    )
    edit_count: Mapped[int] = mapped_column(default=0)
    hidden: Mapped[bool] = mapped_column(default=False)
    hidden_at: Mapped[Optional[datetime]]
    hidden_by_id: Mapped[Optional[UserID]] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    hidden_by: Mapped[Optional[DbUser]] = relationship(
        DbUser, foreign_keys=[hidden_by_id]
    )

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

    topic_id: Mapped[TopicID] = mapped_column(
        db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True
    )
    topic: Mapped[DbTopic] = relationship(
        DbTopic,
        backref=db.backref('initial_topic_posting_association', uselist=False),
    )
    posting_id: Mapped[PostingID] = mapped_column(
        db.Uuid, db.ForeignKey('board_postings.id'), unique=True
    )
    posting: Mapped[DbPosting] = relationship(DbPosting)

    def __init__(self, topic: DbTopic, posting: DbPosting) -> None:
        self.topic = topic
        self.posting = posting
