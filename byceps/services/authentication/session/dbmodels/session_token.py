"""
byceps.services.authentication.session.dbmodels.session_token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from .....database import db
from .....typing import UserID


class SessionToken(db.Model):
    """A user's session token."""

    __tablename__ = 'authn_session_tokens'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    token = db.Column(db.UnicodeText, unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, user_id: UserID, token: str, created_at: datetime
    ) -> None:
        self.user_id = user_id
        self.token = token
        self.created_at = created_at
