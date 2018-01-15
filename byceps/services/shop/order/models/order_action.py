"""
byceps.services.shop.order.models.order_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict

from sqlalchemy.ext.hybrid import hybrid_property

from .....database import db, generate_uuid

from ...article.models.article import Article, ArticleNumber

from .payment import PaymentState


Parameters = Dict[str, Any]


class OrderAction(db.Model):
    """A procedure to execute when an order for that article is marked
    as paid.
    """
    __tablename__ = 'shop_order_actions'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    article_number = db.Column(db.Unicode(20), db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    article = db.relationship(Article, backref='order_actions')
    _payment_state = db.Column('payment_state', db.Unicode(20), index=True, nullable=False)
    procedure = db.Column(db.Unicode(40), nullable=False)
    parameters = db.Column(db.JSONB, nullable=False)

    def __init__(self, article_number: ArticleNumber,
                 payment_state: PaymentState, procedure: str,
                 parameters: Parameters) -> None:
        self.article_number = article_number
        self.payment_state = payment_state
        self.procedure = procedure
        self.parameters = parameters

    @hybrid_property
    def payment_state(self) -> PaymentState:
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state: PaymentState) -> None:
        assert state is not None
        self._payment_state = state.name
