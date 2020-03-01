"""
byceps.services.user_avatar.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from pathlib import Path

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import db, generate_uuid
from ...typing import UserID
from ...util.image.models import ImageType
from ...util.instances import ReprBuilder

from .transfer.models import AvatarID


class Avatar(db.Model):
    """An avatar image uploaded by a user."""

    __tablename__ = 'user_avatars'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    _image_type = db.Column('image_type', db.UnicodeText, nullable=False)

    def __init__(self, creator_id: UserID, image_type: ImageType) -> None:
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
        path = current_app.config['PATH_DATA'] / 'global' / 'users' / 'avatars'
        return path / self.filename

    @property
    def url(self) -> str:
        return f'/data/global/users/avatars/{self.filename}'

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('image_type', self.image_type.name) \
            .build()


class AvatarSelection(db.Model):
    """The selection of an avatar image to be used for a user."""

    __tablename__ = 'user_avatar_selections'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('avatar_selection', uselist=False))
    avatar_id = db.Column(db.Uuid, db.ForeignKey('user_avatars.id'), unique=True, nullable=False)
    avatar = db.relationship(Avatar)

    def __init__(self, user_id: UserID, avatar_id: AvatarID) -> None:
        self.user_id = user_id
        self.avatar_id = avatar_id
