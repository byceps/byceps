"""
byceps.services.authentication.password.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db
from ....typing import UserID


class DbCredential(db.Model):
    """A user's login credential."""

    __tablename__ = 'authn_credentials'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    password_hash = db.Column(db.UnicodeText, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, user_id: UserID, password_hash: str, updated_at: datetime
    ) -> None:
        self.user_id = user_id
        self.password_hash = password_hash
        self.updated_at = updated_at
