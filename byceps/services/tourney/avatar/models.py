"""
byceps.services.tourney.avatar.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from pathlib import Path
from typing import NewType
from uuid import UUID

from flask import current_app, url_for
from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db, generate_uuid
from ....typing import PartyID, UserID
from ....util.image.models import ImageType
from ....util.instances import ReprBuilder


AvatarID = NewType('AvatarID', UUID)


class Avatar(db.Model):
    """A tourney-related avatar image uploaded by a user."""

    __tablename__ = 'tourney_avatars'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    _image_type = db.Column('image_type', db.UnicodeText, nullable=False)

    def __init__(
        self, party_id: PartyID, creator_id: UserID, image_type: ImageType
    ) -> None:
        self.party_id = party_id
        self.creator_id = creator_id
        self.image_type = image_type

    @hybrid_property
    def image_type(self) -> ImageType:
        image_type_str = self._image_type
        if image_type_str is not None:
            return ImageType[image_type_str]

    @image_type.setter
    def image_type(self, image_type: ImageType) -> None:
        self._image_type = image_type.name if (image_type is not None) else None

    @property
    def filename(self) -> Path:
        name_without_suffix = str(self.id)
        suffix = '.' + self.image_type.name
        return Path(name_without_suffix).with_suffix(suffix)

    @property
    def path(self) -> Path:
        path = current_app.config['PATH_TOURNEY_AVATAR_IMAGES']
        return path / self.filename

    @property
    def url(self) -> str:
        path = 'tourney/avatars/{}'.format(self.filename)
        return url_for('party_file', filename=path)

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add('image_type', self.image_type.name) \
            .build()
