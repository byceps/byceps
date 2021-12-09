"""
byceps.services.shop.order.transfer.models.event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from .order import OrderID


OrderEventData = Dict[str, Any]


@dataclass(frozen=True)
class OrderEvent:
    id: UUID
    occurred_at: datetime
    event_type: str
    order_id: OrderID
    data: OrderEventData
