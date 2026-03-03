"""
byceps.services.user.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING

from sqlalchemy.ext.mutable import MutableDict

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.user.models import (
    UserAvatarID,
    UserID,
    USER_DELETED_AVATAR_URL_PATH,
    USER_FALLBACK_AVATAR_URL_PATH,
)
from byceps.util.image.image_type import ImageType
from byceps.util.instances import ReprBuilder


_ABSOLUTE_URL_PATH_PREFIX = '/data/global/users/avatars/'


class DbUserAvatar(db.Model):
    """An avatar image uploaded by a user."""

    __tablename__ = 'user_avatars'

    id: Mapped[UserAvatarID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    _image_type: Mapped[str] = mapped_column('image_type', db.UnicodeText)

    def __init__(
        self,
        avatar_id: UserAvatarID,
        created_at: datetime,
        image_type: ImageType,
    ) -> None:
        self.id = avatar_id
        self.created_at = created_at
        self.image_type = image_type

    @hybrid_property
    def image_type(self) -> ImageType:
        return ImageType[self._image_type]

    @image_type.setter
    def image_type(self, image_type: ImageType) -> None:
        self._image_type = image_type.name

    @property
    def filename(self) -> Path:
        name_without_suffix = str(self.id)
        suffix = '.' + self.image_type.name
        return Path(name_without_suffix).with_suffix(suffix)

    @property
    def url(self) -> str:
        return get_absolute_avatar_url_path(str(self.filename))


def get_absolute_avatar_url_path(filename: str) -> str:
    return _ABSOLUTE_URL_PATH_PREFIX + str(filename)


class DbUser(db.Model):
    """A user."""

    __tablename__ = 'users'

    id: Mapped[UserID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    screen_name: Mapped[str | None] = mapped_column(db.UnicodeText, unique=True)
    email_address: Mapped[str | None] = mapped_column(
        db.UnicodeText, unique=True
    )
    email_address_verified: Mapped[bool]
    avatar_id: Mapped[UserAvatarID | None] = mapped_column(
        db.Uuid, db.ForeignKey('user_avatars.id')
    )
    avatar: Mapped[DbUserAvatar] = relationship(foreign_keys=[avatar_id])
    initialized: Mapped[bool]
    suspended: Mapped[bool]
    deleted: Mapped[bool]
    locale: Mapped[str | None] = mapped_column(db.UnicodeText)
    legacy_id: Mapped[str | None] = mapped_column(db.UnicodeText)

    def __init__(
        self,
        user_id: UserID,
        created_at: datetime,
        screen_name: str | None,
        email_address: str | None,
        *,
        email_address_verified: bool = False,
        initialized: bool = False,
        suspended: bool = False,
        deleted: bool = False,
        locale: str | None = None,
        legacy_id: str | None = None,
    ) -> None:
        self.id = user_id
        self.created_at = created_at
        self.screen_name = screen_name
        self.email_address = email_address
        self.email_address_verified = email_address_verified
        self.initialized = initialized
        self.suspended = suspended
        self.deleted = deleted
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
                'User instance is unhashable because its ID is None.'
            )

        return hash(self.id)

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('screen_name')
            .build()
        )


class DbUserDetail(db.Model):
    """Detailed information about a specific user."""

    __tablename__ = 'user_details'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    user: Mapped[DbUser] = relationship(
        backref=db.backref('detail', uselist=False)
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
