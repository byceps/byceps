"""
byceps.services.authentication.session.dbmodels.recent_login
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.database import db
from byceps.typing import UserID


class DbRecentLogin(db.Model):
    """A user's most recent successful login."""

    __tablename__ = 'authn_recent_logins'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    occurred_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id: UserID, occurred_at: datetime) -> None:
        self.user_id = user_id
        self.occurred_at = occurred_at
