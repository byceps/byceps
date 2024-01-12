"""
byceps.services.authn.session.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.user.models.user import UserID


class DbRecentLogin(db.Model):
    """A user's most recent successful login."""

    __tablename__ = 'authn_recent_logins'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    occurred_at: Mapped[datetime]

    def __init__(self, user_id: UserID, occurred_at: datetime) -> None:
        self.user_id = user_id
        self.occurred_at = occurred_at


class DbSessionToken(db.Model):
    """A user's session token."""

    __tablename__ = 'authn_session_tokens'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    token: Mapped[str] = mapped_column(db.UnicodeText, unique=True, index=True)
    created_at: Mapped[datetime]

    def __init__(
        self, user_id: UserID, token: str, created_at: datetime
    ) -> None:
        self.user_id = user_id
        self.token = token
        self.created_at = created_at
