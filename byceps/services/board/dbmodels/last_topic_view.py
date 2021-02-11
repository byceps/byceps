"""
byceps.services.board.dbmodels.last_topic_view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db
from ....typing import UserID
from ....util.instances import ReprBuilder

from ..transfer.models import TopicID

from .topic import Topic


class LastTopicView(db.Model):
    """The last time a user looked into specific topic."""

    __tablename__ = 'board_topics_lastviews'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True)
    topic = db.relationship(Topic)
    occurred_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, user_id: UserID, topic_id: TopicID, occurred_at: datetime
    ) -> None:
        self.user_id = user_id
        self.topic_id = topic_id
        self.occurred_at = occurred_at

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('user_id') \
            .add('topic', self.topic.title) \
            .add_with_lookup('occurred_at') \
            .build()
