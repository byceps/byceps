"""
byceps.services.user.dbmodels.detail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date
from typing import Any

from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder


class DbUserDetail(db.Model):
    """Detailed information about a specific user."""

    __tablename__ = 'user_details'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    user: Mapped['DbUser'] = relationship(  # noqa: F821, UP037
        'DbUser', backref=db.backref('detail', uselist=False)
    )
    first_name: Mapped[str | None] = mapped_column(db.UnicodeText)
    last_name: Mapped[str | None] = mapped_column(db.UnicodeText)
    date_of_birth: Mapped[date | None]
    country: Mapped[str | None] = mapped_column(db.UnicodeText)
    postal_code: Mapped[str | None] = mapped_column(db.UnicodeText)
    city: Mapped[str | None] = mapped_column(db.UnicodeText)
    street: Mapped[str | None] = mapped_column(db.UnicodeText)
    phone_number: Mapped[str | None] = mapped_column(db.UnicodeText)
    internal_comment: Mapped[str | None] = mapped_column(db.UnicodeText)
    extras: Mapped[dict[str, Any] | None] = mapped_column(
        MutableDict.as_mutable(db.JSONB)
    )

    @property
    def full_name(self) -> str | None:
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)) or None

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('user_id')
            .add_with_lookup('first_name')
            .add_with_lookup('last_name')
            .build()
        )
