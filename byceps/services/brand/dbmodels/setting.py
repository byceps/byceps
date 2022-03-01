"""
byceps.services.brand.dbmodels.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder


class Setting(db.Model):
    """A brand-specific setting."""

    __tablename__ = 'brand_settings'

    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True)
    name = db.Column(db.UnicodeText, primary_key=True)
    value = db.Column(db.UnicodeText)

    def __init__(self, brand_id: BrandID, name: str, value: str) -> None:
        self.brand_id = brand_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('brand_id') \
            .add_with_lookup('name') \
            .add_with_lookup('value') \
            .build()
