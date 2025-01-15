"""
byceps.services.tourney.avatar.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from pathlib import Path
from typing import NewType, TYPE_CHECKING
from uuid import UUID

from flask import current_app
from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID
from byceps.util.image.models import ImageType
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7


AvatarID = NewType('AvatarID', UUID)


class DbTourneyAvatar(db.Model):
    """A tourney-related avatar image uploaded by a user."""

    __tablename__ = 'tourney_avatars'

    id: Mapped[AvatarID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    _image_type: Mapped[str] = mapped_column('image_type', db.UnicodeText)

    def __init__(
        self, party_id: PartyID, creator_id: UserID, image_type: ImageType
    ) -> None:
        self.party_id = party_id
        self.creator_id = creator_id
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
    def path(self) -> Path:
        path = (
            current_app.config['PATH_DATA']
            / 'parties'
            / self.party_id
            / 'tourney'
            / 'avatars'
        )
        return path / self.filename

    @property
    def url_path(self) -> str:
        return f'/data/parties/{self.party_id}/tourney/avatars/{self.filename}'

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('party', self.party_id)
            .add('image_type', self.image_type.name)
            .build()
        )
