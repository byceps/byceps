"""
byceps.services.shop.order.dbmodels.order_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from .....database import db, generate_uuid

from ...article.dbmodels.article import DbArticle
from ...article.transfer.models import ArticleNumber

from ..transfer.action import ActionParameters
from ..transfer.order import PaymentState


class OrderAction(db.Model):
    """A procedure to execute when an order for that article is marked
    as paid.
    """

    __tablename__ = 'shop_order_actions'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    article_number = db.Column(db.UnicodeText, db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    article = db.relationship(DbArticle, backref='order_actions')
    _payment_state = db.Column('payment_state', db.UnicodeText, index=True, nullable=False)
    procedure = db.Column(db.UnicodeText, nullable=False)
    parameters = db.Column(db.JSONB, nullable=False)

    def __init__(
        self,
        article_number: ArticleNumber,
        payment_state: PaymentState,
        procedure: str,
        parameters: ActionParameters,
    ) -> None:
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
