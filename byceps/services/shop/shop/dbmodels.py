"""
byceps.services.shop.shop.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, TYPE_CHECKING

from moneyed import Currency, get_currency
from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict

from byceps.database import db
from byceps.services.brand.models import BrandID
from byceps.util.instances import ReprBuilder

from .models import ShopID


class DbShop(db.Model):
    """A shop."""

    __tablename__ = 'shops'

    id: Mapped[ShopID] = mapped_column(db.UnicodeText, primary_key=True)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('brands.id'),
        unique=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    _currency: Mapped[str] = mapped_column('currency', db.UnicodeText)
    archived: Mapped[bool] = mapped_column(db.Boolean, default=False)
    extra_settings: Mapped[Any | None] = mapped_column(
        MutableDict.as_mutable(db.JSONB)
    )

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
