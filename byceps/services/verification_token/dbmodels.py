"""
byceps.services.verification_token.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
import secrets
from typing import Any, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder

from .models import Purpose


def _generate_token_value():
    """Return a cryptographic, URL-safe token."""
    return secrets.token_urlsafe()


class DbVerificationToken(db.Model):
    """A private token to authenticate as a certain user for a certain
    action.
    """

    __tablename__ = 'verification_tokens'

    token: Mapped[str] = mapped_column(
        db.UnicodeText, default=_generate_token_value, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    _purpose: Mapped[str] = mapped_column('purpose', db.UnicodeText, index=True)
    data: Mapped[Any | None] = mapped_column(db.JSONB)

    def __init__(
        self,
        user_id: UserID,
        purpose: Purpose,
        *,
        data: dict[str, str] | None,
    ) -> None:
        self.user_id = user_id
        self.purpose = purpose
        self.data = data

    @hybrid_property
    def purpose(self) -> Purpose:
        return Purpose[self._purpose]

    @purpose.setter
    def purpose(self, purpose: Purpose) -> None:
        self._purpose = purpose.name

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('token')
            .add('user', self.user.screen_name)
            .add('purpose', self.purpose.name)
            .build()
        )
