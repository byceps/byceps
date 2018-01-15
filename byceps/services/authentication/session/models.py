"""
byceps.services.authentication.session.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import UUID

from ....database import db
from ....typing import UserID


class SessionToken(db.Model):
    """A user's session token."""
    __tablename__ = 'authn_session_tokens'

    token = db.Column(db.Uuid, primary_key=True)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token: UUID, user_id: UserID, created_at: datetime) -> None:
        self.token = token
        self.user_id = user_id
        self.created_at = created_at
