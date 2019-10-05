"""
byceps.services.shop.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....util.instances import ReprBuilder

from .transfer.models import ShopID


class Shop(db.Model):
    """A shop."""

    __tablename__ = 'shops'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    email_config_id = db.Column(db.UnicodeText, db.ForeignKey('email_configs.id'), nullable=False)
    closed = db.Column(db.Boolean, default=False, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self, shop_id: ShopID, title: str, email_config_id: str
    ) -> None:
        self.id = shop_id
        self.title = title
        self.email_config_id = email_config_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
