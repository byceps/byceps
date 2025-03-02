"""
byceps.services.authn.password.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.user.models.user import PasswordHash, UserID


class DbCredential(db.Model):
    """A user's login credential."""

    __tablename__ = 'authn_credentials'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    password_hash: Mapped[str] = mapped_column(db.UnicodeText)
    updated_at: Mapped[datetime]

    def __init__(
        self, user_id: UserID, password_hash: PasswordHash, updated_at: datetime
    ) -> None:
        self.user_id = user_id
        with password_hash.dangerous_reveal() as password_hash:
            self.password_hash = password_hash
        self.updated_at = updated_at
