"""
byceps.services.shop.order.dbmodels.line_item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from .....database import db, generate_uuid

from ...article.dbmodels.article import Article as DbArticle
from ...article.transfer.models import ArticleNumber

from .order import Order


class LineItem(db.Model):
    """A line item that belongs to an order."""

    __tablename__ = 'shop_order_items'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_number = db.Column(db.UnicodeText, db.ForeignKey('shop_orders.order_number'), index=True, nullable=False)
    order = db.relationship(Order, backref='items')
    article_number = db.Column(db.UnicodeText, db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    article = db.relationship(DbArticle, backref='line_items')
    description = db.Column(db.UnicodeText, nullable=False)
    unit_price = db.Column(db.Numeric(6, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity > 0'), nullable=False)
    line_amount = db.Column(db.Numeric(7, 2), nullable=False)
    shipping_required = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        order: Order,
        article_number: ArticleNumber,
        description: str,
        unit_price: Decimal,
        tax_rate: Decimal,
        quantity: int,
        line_amount: Decimal,
        shipping_required: bool,
    ) -> None:
        # Require order instance rather than order number as argument
        # because line items are created together with the order – and
        # until the order is created, there is no order number assigned.
        self.order = order
        self.article_number = article_number
        self.description = description
        self.unit_price = unit_price
        self.tax_rate = tax_rate
        self.quantity = quantity
        self.line_amount = line_amount
        self.shipping_required = shipping_required