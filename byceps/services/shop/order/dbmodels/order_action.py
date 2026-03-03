"""
byceps.services.shop.order.dbmodels.order_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.order.models.action import ActionParameters


class DbOrderAction(db.Model):
    """A procedure to execute when an order for that product is marked
    as paid.
    """

    __tablename__ = 'shop_order_actions'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    product: Mapped[DbProduct] = relationship(backref='order_actions')
    procedure: Mapped[str] = mapped_column(db.UnicodeText)
    parameters: Mapped[ActionParameters] = mapped_column(db.JSONB)

    def __init__(
        self,
        action_id: UUID,
        product_id: ProductID,
        procedure: str,
        parameters: ActionParameters,
    ) -> None:
        self.id = action_id
        self.product_id = product_id
        self.procedure = procedure
        self.parameters = parameters
