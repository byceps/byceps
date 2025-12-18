"""
byceps.services.user.dbmodels.avatar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.user.models.user import UserAvatarID
from byceps.util.image.image_type import ImageType
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7


_ABSOLUTE_URL_PATH_PREFIX = '/data/global/users/avatars/'


class DbUserAvatar(db.Model):
    """An avatar image uploaded by a user."""

    __tablename__ = 'user_avatars'

    id: Mapped[UserAvatarID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    created_at: Mapped[datetime]
    _image_type: Mapped[str] = mapped_column('image_type', db.UnicodeText)

    def __init__(self, created_at: datetime, image_type: ImageType) -> None:
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
        return get_absolute_url_path(str(self.filename))

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('image_type', self.image_type.name)
            .build()
        )


def get_absolute_url_path(filename: str) -> str:
    return _ABSOLUTE_URL_PATH_PREFIX + str(filename)
