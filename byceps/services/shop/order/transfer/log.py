"""
byceps.services.shop.order.transfer.log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from .order import OrderID


OrderLogEntryData = dict[str, Any]


@dataclass(frozen=True)
class OrderLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    order_id: OrderID
    data: OrderLogEntryData
