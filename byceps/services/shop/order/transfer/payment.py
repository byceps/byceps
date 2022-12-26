"""
byceps.services.shop.order.transfer.payment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .....util.money import Money

from .order import OrderID


AdditionalPaymentData = dict[str, str]


@dataclass(frozen=True)
class Payment:
    id: UUID
    order_id: OrderID
    created_at: datetime
    method: str
    amount: Money
    additional_data: AdditionalPaymentData
