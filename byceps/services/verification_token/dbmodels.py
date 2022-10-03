"""
byceps.services.verification_token.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
import secrets
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from ...database import db
from ...typing import UserID
from ...util.instances import ReprBuilder

from .transfer.models import Purpose


def _generate_token_value():
    """Return a cryptographic, URL-safe token."""
    return secrets.token_urlsafe()


class DbVerificationToken(db.Model):
    """A private token to authenticate as a certain user for a certain
    action.
    """

    __tablename__ = 'verification_tokens'

    token = db.Column(db.UnicodeText, default=_generate_token_value, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    _purpose = db.Column('purpose', db.UnicodeText, index=True, nullable=False)
    data = db.Column(db.JSONB, nullable=True)

    def __init__(
        self,
        user_id: UserID,
        purpose: Purpose,
        *,
        data: Optional[dict[str, str]],
    ) -> None:
        self.user_id = user_id
        self.purpose = purpose
        self.data = data

    @hybrid_property
    def purpose(self) -> Purpose:
        return Purpose[self._purpose]

    @purpose.setter
    def purpose(self, purpose: Purpose) -> None:
        assert purpose is not None
        self._purpose = purpose.name

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('token') \
            .add('user', self.user.screen_name) \
            .add('purpose', self.purpose.name) \
            .build()
