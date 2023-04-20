"""
byceps.services.shop.order.dbmodels.order_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db, generate_uuid4
from byceps.services.shop.article.dbmodels.article import DbArticle
from byceps.services.shop.article.models import ArticleID
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import PaymentState


class DbOrderAction(db.Model):
    """A procedure to execute when an order for that article is marked
    as paid.
    """

    __tablename__ = 'shop_order_actions'

    id = db.Column(db.Uuid, default=generate_uuid4, primary_key=True)
    article_id = db.Column(
        db.Uuid, db.ForeignKey('shop_articles.id'), index=True, nullable=False
    )
    article = db.relationship(DbArticle, backref='order_actions')
    _payment_state = db.Column(
        'payment_state', db.UnicodeText, index=True, nullable=False
    )
    procedure = db.Column(db.UnicodeText, nullable=False)
    parameters = db.Column(db.JSONB, nullable=False)

    def __init__(
        self,
        article_id: ArticleID,
        payment_state: PaymentState,
        procedure: str,
        parameters: ActionParameters,
    ) -> None:
        self.article_id = article_id
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
