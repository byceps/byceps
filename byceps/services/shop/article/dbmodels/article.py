"""
byceps.services.shop.article.dbmodels.article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from .....database import BaseQuery, db, generate_uuid
from .....util.instances import ReprBuilder

from ...shop.transfer.models import ShopID

from ..transfer.models import ArticleNumber


class ArticleQuery(BaseQuery):

    def for_shop(self, shop_id: ShopID) -> BaseQuery:
        return self.filter_by(shop_id=shop_id)

    def currently_available(self) -> BaseQuery:
        """Select only articles that are available in between the
        temporal boundaries for this article, if specified.
        """
        now = datetime.utcnow()

        return self \
            .filter(db.or_(
                Article.available_from == None,
                now >= Article.available_from
            )) \
            .filter(db.or_(
                Article.available_until == None,
                now < Article.available_until
            ))


class Article(db.Model):
    """An article that can be bought."""

    __tablename__ = 'shop_articles'
    __table_args__ = (
        db.UniqueConstraint('shop_id', 'description'),
        db.CheckConstraint('available_from < available_until'),
    )
    query_class = ArticleQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    shop_id = db.Column(db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False)
    item_number = db.Column(db.UnicodeText, unique=True, nullable=False)
    description = db.Column(db.UnicodeText, nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    available_from = db.Column(db.DateTime, nullable=True)
    available_until = db.Column(db.DateTime, nullable=True)
    total_quantity = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity >= 0'), nullable=False)
    max_quantity_per_order = db.Column(db.Integer, nullable=False)
    not_directly_orderable = db.Column(db.Boolean, default=False, nullable=False)
    requires_separate_order = db.Column(db.Boolean, default=False, nullable=False)
    shipping_required = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        shop_id: ShopID,
        item_number: ArticleNumber,
        description: str,
        price: Decimal,
        tax_rate: Decimal,
        total_quantity: int,
        max_quantity_per_order: int,
        *,
        available_from: Optional[datetime] = None,
        available_until: Optional[datetime] = None,
    ) -> None:
        self.shop_id = shop_id
        self.item_number = item_number
        self.description = description
        self.price = price
        self.tax_rate = tax_rate
        self.available_from = available_from
        self.available_until = available_until
        self.total_quantity = total_quantity
        self.quantity = total_quantity  # Initialize with total quantity.
        self.max_quantity_per_order = max_quantity_per_order

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('shop', self.shop_id) \
            .add_with_lookup('item_number') \
            .add_with_lookup('description') \
            .build()
