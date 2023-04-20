"""
byceps.services.shop.cancelation_request.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db, generate_uuid7
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder

from .models import CancelationRequestState, DonationExtent


class DbCancelationRequest(db.Model):
    """A request for cancelation of an order.

    The amount can be chosen to fully donated, fully refunded, or
    partially donated and refuned.
    """

    __tablename__ = 'shop_order_cancelation_requests'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    shop_id = db.Column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False
    )
    order_number = db.Column(
        db.UnicodeText,
        db.ForeignKey('shop_orders.order_number'),
        unique=True,
        nullable=False,
    )
    _donation_extent = db.Column(
        'donation_extent', db.UnicodeText, index=True, nullable=False
    )
    amount_refund = db.Column(db.Numeric(7, 2), nullable=False)
    amount_donation = db.Column(db.Numeric(7, 2), nullable=False)
    recipient_name = db.Column(db.UnicodeText, nullable=True)
    recipient_iban = db.Column(db.UnicodeText, nullable=True)
    _state = db.Column('state', db.UnicodeText, index=True, nullable=False)

    def __init__(
        self,
        created_at: datetime,
        shop_id: ShopID,
        order_number: OrderNumber,
        donation_extent: DonationExtent,
        amount_refund: Decimal,
        amount_donation: Decimal,
        recipient_name: Optional[str],
        recipient_iban: Optional[str],
    ) -> None:
        self.created_at = created_at
        self.shop_id = shop_id
        self.order_number = order_number
        self.donation_extent = donation_extent
        self.amount_refund = amount_refund
        self.amount_donation = amount_donation
        self.recipient_name = recipient_name
        self.recipient_iban = recipient_iban
        self.state = CancelationRequestState.open

    @hybrid_property
    def donation_extent(self) -> DonationExtent:
        return DonationExtent[self._donation_extent]

    @donation_extent.setter
    def donation_extent(self, donation_extent: DonationExtent) -> None:
        self._donation_extent = donation_extent.name

    @hybrid_property
    def state(self) -> CancelationRequestState:
        return CancelationRequestState[self._state]

    @state.setter
    def state(self, state: CancelationRequestState) -> None:
        self._state = state.name

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('order_number')
            .build()
        )
