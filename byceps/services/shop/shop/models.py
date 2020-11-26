"""
byceps.services.shop.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.mutable import MutableDict

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder

from .transfer.models import ShopID


class Shop(db.Model):
    """A shop."""

    __tablename__ = 'shops'

    id = db.Column(db.UnicodeText, primary_key=True)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), index=True, nullable=False)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    email_config_id = db.Column(db.UnicodeText, db.ForeignKey('email_configs.id'), nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    extra_settings = db.Column(MutableDict.as_mutable(db.JSONB))

    def __init__(
        self,
        shop_id: ShopID,
        brand_id: BrandID,
        title: str,
        email_config_id: str,
    ) -> None:
        self.id = shop_id
        self.brand_id = brand_id
        self.title = title
        self.email_config_id = email_config_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
