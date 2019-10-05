"""
byceps.services.user_badge.models.badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db, generate_uuid
from ....typing import BrandID
from ....util.instances import ReprBuilder


class Badge(db.Model):
    """A global badge that can be awarded to a user."""

    __tablename__ = 'user_badges'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), nullable=True)
    slug = db.Column(db.UnicodeText, unique=True, index=True, nullable=False)
    label = db.Column(db.UnicodeText, unique=True, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    image_filename = db.Column(db.UnicodeText, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        slug: str,
        label: str,
        image_filename: str,
        *,
        brand_id: Optional[BrandID] = None,
        description: Optional[str] = None,
        featured: bool = False,
    ) -> None:
        self.brand_id = brand_id
        self.slug = slug
        self.label = label
        self.description = description
        self.image_filename = image_filename
        self.featured = featured

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('brand_id') \
            .add_with_lookup('label') \
            .build()
