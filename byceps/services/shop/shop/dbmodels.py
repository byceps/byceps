"""
byceps.services.shop.shop.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import TYPE_CHECKING

from moneyed import Currency, get_currency


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict

from byceps.database import db
from byceps.typing import BrandID
from byceps.util.instances import ReprBuilder

from .models import ShopID


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
    _currency = db.Column('currency', db.UnicodeText, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    extra_settings = db.Column(MutableDict.as_mutable(db.JSONB))

    def __init__(
        self, shop_id: ShopID, brand_id: BrandID, title: str, currency: Currency
    ) -> None:
        self.id = shop_id
        self.brand_id = brand_id
        self.title = title
        self.currency = currency

    @hybrid_property
    def currency(self) -> Currency:
        return get_currency(self._currency)

    @currency.setter
    def currency(self, currency: Currency) -> None:
        self._currency = currency.code

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()
