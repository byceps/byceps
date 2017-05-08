"""
byceps.services.user_badge.models.badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from flask import url_for

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder


class Badge(db.Model):
    """A global badge that can be awarded to a user."""
    __tablename__ = 'user_badges'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), nullable=True)
    label = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    image_filename = db.Column(db.Unicode(80), nullable=False)

    def __init__(self, label, image_filename, *, brand_id=None, description=None):
        self.brand_id = brand_id
        self.label = label
        self.description = description
        self.image_filename = image_filename

    @property
    def image_url(self):
        filename = 'users/badges/{}'.format(self.image_filename)
        return url_for('global_file', filename=filename)

    def to_tuple(self):
        """Return a tuple representation of this entity."""
        return BadgeTuple(
            self.id,
            self.brand_id,
            self.label,
            self.description,
            self.image_url
        )

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('brand_id') \
            .add_with_lookup('label') \
            .build()


BadgeTuple = namedtuple('BadgeTuple',
    'id, brand_id, label, description, image_url')
