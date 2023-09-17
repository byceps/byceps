"""
byceps.services.brand.dbmodels.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.typing import BrandID
from byceps.util.instances import ReprBuilder


class DbSetting(db.Model):
    """A brand-specific setting."""

    __tablename__ = 'brand_settings'

    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    value: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, brand_id: BrandID, name: str, value: str) -> None:
        self.brand_id = brand_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('brand_id')
            .add_with_lookup('name')
            .add_with_lookup('value')
            .build()
        )
