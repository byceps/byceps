"""
byceps.services.brand.dbmodels.brand
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder


class DbBrand(db.Model):
    """A party brand."""

    __tablename__ = 'brands'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    image_filename = db.Column(db.UnicodeText, nullable=True)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        brand_id: BrandID,
        title: str,
        *,
        image_filename: Optional[str] = None,
    ) -> None:
        self.id = brand_id
        self.title = title
        self.image_filename = image_filename

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
