"""
byceps.services.shop.cancelation_request.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.shop.models import ShopID


DonationExtent = Enum(
    'DonationExtent',
    [
        'everything',
        'part',
        'nothing',
    ],
)


CancelationRequestState = Enum(
    'CancelationRequestState',
    [
        'open',
        'accepted',
        'denied',
    ],
)


@dataclass(frozen=True)
class CancelationRequest:
    id: UUID
    created_at: datetime
    shop_id: ShopID
    order_number: OrderNumber
    donation_extent: DonationExtent
    amount_refund: Decimal
    amount_donation: Decimal
    recipient_name: str | None
    recipient_iban: str | None
    state: CancelationRequestState


@dataclass(frozen=True)
class CancelationRequestQuantitiesByState:
    open: int
    accepted: int
    denied: int
    total: int
