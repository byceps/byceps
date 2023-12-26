"""
byceps.services.shop.cancellation_request.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import OrderID
from byceps.services.shop.shop.models import ShopID


DonationExtent = Enum(
    'DonationExtent',
    [
        'everything',
        'part',
        'nothing',
    ],
)


CancellationRequestState = Enum(
    'CancellationRequestState',
    [
        'open',
        'accepted',
        'denied',
    ],
)


@dataclass(frozen=True)
class CancellationRequest:
    id: UUID
    created_at: datetime
    shop_id: ShopID
    order_id: OrderID
    order_number: OrderNumber
    donation_extent: DonationExtent
    amount_refund: Decimal
    amount_donation: Decimal
    recipient_name: str | None
    recipient_iban: str | None
    state: CancellationRequestState


@dataclass(frozen=True)
class CancellationRequestQuantitiesByState:
    open: int
    accepted: int
    denied: int
    total: int
