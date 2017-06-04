"""
byceps.services.user_badge.models.badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from typing import NewType, Optional
from uuid import UUID

from flask import url_for

from ....database import db, generate_uuid
from ....typing import BrandID
from ....util.instances import ReprBuilder


BadgeID = NewType('BadgeID', UUID)


BadgeTuple = namedtuple('BadgeTuple',
    'id, brand_id, label, description, image_url')


class Badge(db.Model):
    """A global badge that can be awarded to a user."""
    __tablename__ = 'user_badges'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), nullable=True)
    label = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    image_filename = db.Column(db.Unicode(80), nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, label: str, image_filename: str, *,
                 brand_id: Optional[BrandID]=None,
                 description: Optional[str]=None,
                 is_featured: bool=False) -> None:
        self.brand_id = brand_id
        self.label = label
        self.description = description
        self.image_filename = image_filename
        self.is_featured = is_featured

    @property
    def image_url(self) -> str:
        filename = 'users/badges/{}'.format(self.image_filename)
        return url_for('global_file', filename=filename)

    def to_tuple(self) -> BadgeTuple:
        """Return a tuple representation of this entity."""
        return BadgeTuple(
            self.id,
            self.brand_id,
            self.label,
            self.description,
            self.image_url
        )

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('brand_id') \
            .add_with_lookup('label') \
            .build()
