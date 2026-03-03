"""
byceps.services.tourney.dbmodels.avatar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
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

from byceps.byceps_app import get_current_byceps_app
from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.tourney.models import TourneyAvatarID
from byceps.services.user.models import UserID
from byceps.util.image.image_type import ImageType


class DbTourneyAvatar(db.Model):
    """A tourney-related avatar image uploaded by a user."""

    __tablename__ = 'tourney_avatars'

    id: Mapped[TourneyAvatarID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    _image_type: Mapped[str] = mapped_column('image_type', db.UnicodeText)

    def __init__(
        self,
        avatar_id: TourneyAvatarID,
        party_id: PartyID,
        created_at: datetime,
        creator_id: UserID,
        image_type: ImageType,
    ) -> None:
        self.id = avatar_id
        self.party_id = party_id
        self.created_at = created_at
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
            get_current_byceps_app().byceps_config.data_path
            / 'parties'
            / self.party_id
            / 'tourney'
            / 'avatars'
        )
        return path / self.filename

    @property
    def url_path(self) -> str:
        return f'/data/parties/{self.party_id}/tourney/avatars/{self.filename}'
