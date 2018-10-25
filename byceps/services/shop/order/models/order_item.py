"""
byceps.services.shop.order.models.order_item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from .....database import db, generate_uuid

from ...article.models.article import Article
from ...article.transfer.models import ArticleNumber

from ..transfer.models import OrderItem as OrderItemTransferObject

from .order import Order


class OrderItem(db.Model):
    """An item that belongs to an order."""
    __tablename__ = 'shop_order_items'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_number = db.Column(db.Unicode(13), db.ForeignKey('shop_orders.order_number'), index=True, nullable=False)
    order = db.relationship(Order, backref='items')
    article_number = db.Column(db.Unicode(20), db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    article = db.relationship(Article, backref='order_items')
    description = db.Column(db.Unicode(80), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity > 0'), nullable=False)
    shipping_required = db.Column(db.Boolean, nullable=False)

    def __init__(self, order: Order, article_number: ArticleNumber,
                 description: str, price: Decimal, tax_rate: Decimal,
                 quantity: int, shipping_required: bool) -> None:
        # Require order instance rather than order number as argument
        # because order items are created together with the order – and
        # until the order is created, there is no order number assigned.
        self.order = order
        self.article_number = article_number
        self.description = description
        self.price = price
        self.tax_rate = tax_rate
        self.quantity = quantity
        self.shipping_required = shipping_required

    @classmethod
    def from_article(cls, order: Order, article: Article, quantity: int
                    ) -> 'OrderItem':
        return cls(
            order,
            article.item_number,
            article.description,
            article.price,
            article.tax_rate,
            quantity,
            article.shipping_required,
        )


    @property
    def unit_price(self) -> Decimal:
        return self.price

    @property
    def line_price(self) -> Decimal:
        return self.unit_price * self.quantity

    def to_transfer_object(self) -> OrderItemTransferObject:
        return OrderItemTransferObject(
            self.order_number,
            self.article_number,
            self.description,
            self.unit_price,
            self.tax_rate,
            self.quantity,
            self.line_price,
        )
