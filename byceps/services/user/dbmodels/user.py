"""
byceps.services.user.dbmodels.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.user.models.user import (
    UserAvatarID,
    UserID,
    USER_DELETED_AVATAR_URL_PATH,
    USER_FALLBACK_AVATAR_URL_PATH,
)
from byceps.util.instances import ReprBuilder

from .avatar import DbUserAvatar


class DbUser(db.Model):
    """A user."""

    __tablename__ = 'users'

    id: Mapped[UserID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    screen_name: Mapped[str | None] = mapped_column(db.UnicodeText, unique=True)
    email_address: Mapped[str | None] = mapped_column(
        db.UnicodeText, unique=True
    )
    email_address_verified: Mapped[bool] = mapped_column(default=False)
    avatar_id: Mapped[UserAvatarID | None] = mapped_column(
        db.Uuid, db.ForeignKey('user_avatars.id')
    )
    avatar: Mapped[DbUserAvatar] = relationship(
        DbUserAvatar, foreign_keys=[avatar_id]
    )
    initialized: Mapped[bool] = mapped_column(default=False)
    suspended: Mapped[bool] = mapped_column(default=False)
    deleted: Mapped[bool] = mapped_column(default=False)
    locale: Mapped[str | None] = mapped_column(db.UnicodeText)
    legacy_id: Mapped[str | None] = mapped_column(db.UnicodeText)

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
        if self.avatar:
            return self.avatar.url
        elif self.deleted:
            return USER_DELETED_AVATAR_URL_PATH
        else:
            return USER_FALLBACK_AVATAR_URL_PATH

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
