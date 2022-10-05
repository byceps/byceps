"""
byceps.services.shop.shop.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.mutable import MutableDict

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder

from .transfer.models import ShopID


class DbShop(db.Model):
    """A shop."""

    __tablename__ = 'shops'

    id = db.Column(db.UnicodeText, primary_key=True)
    brand_id = db.Column(
        db.UnicodeText,
        db.ForeignKey('brands.id'),
        unique=True,
        index=True,
        nullable=False,
    )
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    extra_settings = db.Column(MutableDict.as_mutable(db.JSONB))

    def __init__(self, shop_id: ShopID, brand_id: BrandID, title: str) -> None:
        self.id = shop_id
        self.brand_id = brand_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
