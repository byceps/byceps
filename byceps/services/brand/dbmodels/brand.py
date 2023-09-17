"""
byceps.services.brand.dbmodels.brand
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.typing import BrandID
from byceps.util.instances import ReprBuilder


class DbBrand(db.Model):
    """A party brand."""

    __tablename__ = 'brands'

    id: Mapped[BrandID] = mapped_column(db.UnicodeText, primary_key=True)
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    image_filename: Mapped[str | None] = mapped_column(db.UnicodeText)
    archived: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        brand_id: BrandID,
        title: str,
        *,
        image_filename: str | None = None,
    ) -> None:
        self.id = brand_id
        self.title = title
        self.image_filename = image_filename

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()
