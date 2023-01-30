"""
byceps.services.tourney.dbmodels.match_comment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db, generate_uuid7
from ....typing import UserID

from ...user.dbmodels.user import DbUser

from ..models import MatchID

from .match import DbMatch


class DbMatchComment(db.Model):
    """An immutable comment on a match by one of the opponents."""

    __tablename__ = 'tourney_match_comments'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    match_id = db.Column(
        db.Uuid, db.ForeignKey('tourney_matches.id'), index=True, nullable=False
    )
    match = db.relationship(DbMatch)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), nullable=False
    )
    created_by = db.relationship(DbUser, foreign_keys=[created_by_id])
    body = db.Column(db.UnicodeText, nullable=False)
    last_edited_at = db.Column(db.DateTime)
    last_edited_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_edited_by = db.relationship(DbUser, foreign_keys=[last_edited_by_id])
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(DbUser, foreign_keys=[hidden_by_id])

    def __init__(
        self, match_id: MatchID, creator_id: UserID, body: str
    ) -> None:
        self.match_id = match_id
        self.created_by_id = creator_id
        self.body = body
