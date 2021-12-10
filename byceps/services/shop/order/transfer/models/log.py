"""
byceps.services.shop.order.transfer.models.log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from .order import OrderID


OrderLogEntryData = Dict[str, Any]


@dataclass(frozen=True)
class OrderLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    order_id: OrderID
    data: OrderLogEntryData
