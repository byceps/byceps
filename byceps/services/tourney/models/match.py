"""
byceps.services.tourney.models.match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID


from ....database import BaseQuery, db, generate_uuid
from ....typing import UserID

from ...user.models.user import User


MatchID = NewType('MatchID', UUID)


class Match(db.Model):
    """A match between two opponents."""

    __tablename__ = 'tourney_matches'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)


MatchCommentID = NewType('MatchCommentID', UUID)


class MatchCommentQuery(BaseQuery):

    def for_match(self, match_id: MatchID) -> BaseQuery:
        return self.filter_by(match_id=match_id)


class MatchComment(db.Model):
    """An immutable comment on a match by one of the opponents."""

    __tablename__ = 'tourney_match_comments'
    query_class = MatchCommentQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    match_id = db.Column(db.Uuid, db.ForeignKey('tourney_matches.id'), index=True, nullable=False)
    match = db.relationship(Match)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship(User, foreign_keys=[created_by_id])
    body = db.Column(db.UnicodeText, nullable=False)
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(User, foreign_keys=[hidden_by_id])

    def __init__(
        self, match_id: MatchID, creator_id: UserID, body: str
    ) -> None:
        self.match_id = match_id
        self.created_by_id = creator_id
        self.body = body
