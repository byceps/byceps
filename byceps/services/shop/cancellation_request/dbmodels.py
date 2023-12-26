"""
byceps.services.shop.cancellation_request.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import OrderID
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .models import CancellationRequestState, DonationExtent


class DbCancellationRequest(db.Model):
    """A request for cancellation of an order.

    The amount can be chosen to fully donated, fully refunded, or
    partially donated and refuned.
    """

    __tablename__ = 'shop_order_cancellation_requests'

    id: Mapped[UUID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    created_at: Mapped[datetime]
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    order_id: Mapped[OrderID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_orders.id'), unique=True
    )
    order_number: Mapped[OrderNumber] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_orders.order_number'),
        unique=True,
        nullable=False,
    )
    _donation_extent: Mapped[str] = mapped_column(
        'donation_extent', db.UnicodeText, index=True
    )
    amount_refund: Mapped[Decimal] = mapped_column(db.Numeric(7, 2))
    amount_donation: Mapped[Decimal] = mapped_column(db.Numeric(7, 2))
    recipient_name: Mapped[str | None] = mapped_column(db.UnicodeText)
    recipient_iban: Mapped[str | None] = mapped_column(db.UnicodeText)
    _state: Mapped[str] = mapped_column('state', db.UnicodeText, index=True)

    def __init__(
        self,
        created_at: datetime,
        shop_id: ShopID,
        order_id: OrderID,
        order_number: OrderNumber,
        donation_extent: DonationExtent,
        amount_refund: Decimal,
        amount_donation: Decimal,
        recipient_name: str | None,
        recipient_iban: str | None,
    ) -> None:
        self.created_at = created_at
        self.shop_id = shop_id
        self.order_id = order_id
        self.order_number = order_number
        self.donation_extent = donation_extent
        self.amount_refund = amount_refund
        self.amount_donation = amount_donation
        self.recipient_name = recipient_name
        self.recipient_iban = recipient_iban
        self.state = CancellationRequestState.open

    @hybrid_property
    def donation_extent(self) -> DonationExtent:
        return DonationExtent[self._donation_extent]

    @donation_extent.setter
    def donation_extent(self, donation_extent: DonationExtent) -> None:
        self._donation_extent = donation_extent.name

    @hybrid_property
    def state(self) -> CancellationRequestState:
        return CancellationRequestState[self._state]

    @state.setter
    def state(self, state: CancellationRequestState) -> None:
        self._state = state.name

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('order_number')
            .build()
        )
