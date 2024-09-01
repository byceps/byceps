"""
byceps.services.shop.order.dbmodels.order_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import PaymentState


class DbOrderAction(db.Model):
    """A procedure to execute when an order for that product is marked
    as paid.
    """

    __tablename__ = 'shop_order_actions'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    product: Mapped[DbProduct] = relationship(
        DbProduct, backref='order_actions'
    )
    _payment_state: Mapped[str] = mapped_column(
        'payment_state', db.UnicodeText, index=True
    )
    procedure: Mapped[str] = mapped_column(db.UnicodeText)
    parameters: Mapped[ActionParameters] = mapped_column(db.JSONB)

    def __init__(
        self,
        action_id: UUID,
        product_id: ProductID,
        payment_state: PaymentState,
        procedure: str,
        parameters: ActionParameters,
    ) -> None:
        self.id = action_id
        self.product_id = product_id
        self.payment_state = payment_state
        self.procedure = procedure
        self.parameters = parameters

    @hybrid_property
    def payment_state(self) -> PaymentState:
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state: PaymentState) -> None:
        self._payment_state = state.name
