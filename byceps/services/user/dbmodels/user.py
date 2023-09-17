"""
byceps.services.user.dbmodels.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.user.models.user import UserAvatarID
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder

from .avatar import DbUserAvatar


class DbUser(db.Model):
    """A user."""

    __tablename__ = 'users'

    id: Mapped[UserID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    screen_name: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText, unique=True
    )
    email_address: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText, unique=True
    )
    email_address_verified: Mapped[bool] = mapped_column(default=False)
    avatar_id: Mapped[Optional[UserAvatarID]] = mapped_column(  # noqa: UP007
        db.Uuid, db.ForeignKey('user_avatars.id')
    )
    avatar: Mapped[DbUserAvatar] = relationship(
        DbUserAvatar, foreign_keys=[avatar_id]
    )
    initialized: Mapped[bool] = mapped_column(default=False)
    suspended: Mapped[bool] = mapped_column(default=False)
    deleted: Mapped[bool] = mapped_column(default=False)
    locale: Mapped[Optional[str]] = mapped_column(db.UnicodeText)  # noqa: UP007
    legacy_id: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )

    def __init__(
        self,
        user_id: UserID,
        created_at: datetime,
        screen_name: str | None,
        email_address: str | None,
        *,
        locale: str | None = None,
        legacy_id: str | None = None,
    ) -> None:
        self.id = user_id
        self.created_at = created_at
        self.screen_name = screen_name
        self.email_address = email_address
        self.locale = locale
        self.legacy_id = legacy_id

    @property
    def avatar_url(self) -> str | None:
        avatar = self.avatar
        return avatar.url if (avatar is not None) else None

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)

    def __hash__(self) -> int:
        if self.id is None:
            raise ValueError(
                'User instance is unhashable because its id is None.'
            )

        return hash(self.id)

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('screen_name')
            .build()
        )
