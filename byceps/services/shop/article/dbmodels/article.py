"""
byceps.services.shop.article.dbmodels.article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from moneyed import Currency, get_currency, Money

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from .....database import db, generate_uuid
from .....util.instances import ReprBuilder

from ...shop.transfer.models import ShopID

from ..transfer.models import ArticleNumber, ArticleType, ArticleTypeParams


class DbArticle(db.Model):
    """An article that can be bought."""

    __tablename__ = 'shop_articles'
    __table_args__ = (
        db.UniqueConstraint('shop_id', 'description'),
        db.CheckConstraint('available_from < available_until'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    shop_id = db.Column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False
    )
    item_number = db.Column(db.UnicodeText, unique=True, nullable=False)
    _type = db.Column('type', db.UnicodeText, nullable=False)
    type_params = db.Column(db.JSONB, nullable=True)
    description = db.Column(db.UnicodeText, nullable=False)
    price_amount = db.Column(db.Numeric(6, 2), nullable=False)
    _price_currency = db.Column(
        'price_currency', db.UnicodeText, nullable=False
    )
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    available_from = db.Column(db.DateTime, nullable=True)
    available_until = db.Column(db.DateTime, nullable=True)
    total_quantity = db.Column(db.Integer, nullable=False)
    quantity = db.Column(
        db.Integer, db.CheckConstraint('quantity >= 0'), nullable=False
    )
    max_quantity_per_order = db.Column(db.Integer, nullable=False)
    not_directly_orderable = db.Column(
        db.Boolean, default=False, nullable=False
    )
    separate_order_required = db.Column(
        db.Boolean, default=False, nullable=False
    )
    processing_required = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        shop_id: ShopID,
        item_number: ArticleNumber,
        type_: ArticleType,
        description: str,
        price: Money,
        tax_rate: Decimal,
        total_quantity: int,
        max_quantity_per_order: int,
        processing_required: bool,
        *,
        type_params: Optional[ArticleTypeParams] = None,
        available_from: Optional[datetime] = None,
        available_until: Optional[datetime] = None,
    ) -> None:
        self.shop_id = shop_id
        self.item_number = item_number
        self._type = type_.name
        self.type_params = type_params
        self.description = description
        self.price_amount = price.amount
        self.price_currency = price.currency
        self.tax_rate = tax_rate
        self.available_from = available_from
        self.available_until = available_until
        self.total_quantity = total_quantity
        self.quantity = total_quantity  # Initialize with total quantity.
        self.max_quantity_per_order = max_quantity_per_order
        self.processing_required = processing_required

    @hybrid_property
    def type_(self) -> ArticleType:
        return ArticleType[self._type]

    @hybrid_property
    def price_currency(self) -> Currency:
        return get_currency(self._price_currency)

    @price_currency.setter
    def price_currency(self, currency: Currency) -> None:
        self._price_currency = currency.code

    @property
    def price(self) -> Money:
        return Money(self.price_amount, self.price_currency)

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('item_number')
            .add_with_lookup('description')
            .build()
        )
