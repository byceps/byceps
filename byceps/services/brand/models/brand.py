"""
byceps.services.brand.models.brand
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder


class Brand(db.Model):
    """A party brand."""

    __tablename__ = 'brands'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)

    def __init__(self, brand_id: BrandID, title: str) -> None:
        self.id = brand_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
